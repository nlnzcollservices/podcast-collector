import tkinter as tk
from tkinter import ttk, messagebox,filedialog, scrolledtext
from tkhtmlview import HTMLLabel
import tkcalendar as tkc
from datetime import datetime as dt
from PIL import Image, ImageTk
import os
import sys
import shutil
from tkinterweb import HtmlFrame
from PIL import Image, ImageTk
from podcasts import Podcast_pipeline
from podcasts1_create_record import RecordCreator
from podcasts0_harvester import harvest
from podcasts2_make_sips import sip_routine
from podcast_dict import podcasts_dict, serials
from podcasts_database_handler import DbHandler
from settings import logging, creds, podcast_sprsh, database_archived_folder, database_fullname, file_folder, report_folder, sip_folder, rosetta_folder, client_secrets_file, archived_folder, doc_folder, ndha_report_folder, ndha_used_report_folder, my_email_box, report_part_name, done_ies, failed_ies
from query_read_db_to_csv import export_data_to_csv
from query_possibly_ceased import find_podcast_with_last_episode_harvested_before_date
from query_find_title import find_episode_by_pattern
from query_delete_episode_by_id import delete_episode_by_id
from read_episode_from_googlesheet_to_db import ReadFromSpreadsheet
from podcasts_cleaning_scripts  import PodcastCleaningPipeline
pc = PodcastCleaningPipeline()
scheme_path = os.path.join(doc_folder, "podcasts_GUI.png") 
cleaning_scheme_path = os.path.join(doc_folder, "podcasts_cleaning.png")





class PodcastPipelineGUI(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Podcast Pipeline GUI")
        self.geometry(f"{self.winfo_screenwidth()}x{int(self.winfo_screenheight() * 0.9)}")  # Adjust the height to 90% of the screen height

        # Default key is 'prod'
        self.key = "prod"
        self.create_widgets()

    def create_widgets(self):
        # Tab control
        self.tab_control = ttk.Notebook(self)

        # First tab - Actions
        self.actions_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.actions_tab, text='Actions')

        # Second tab - Cleaning Scripts
        self.cleaning_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.cleaning_tab, text='Cleaning')
        self.create_cleaning_tab()

        # Third tab - Documentation
        documentation_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(documentation_tab, text='Documentation')
        self.create_documentation_tab(documentation_tab)

        self.tab_control.pack(expand=True, fill="both")

        self.create_actions_tab()
        self.create_log_textbox()

    def create_actions_tab(self):
        # Left frame for actions
        left_frame = tk.Frame(self.actions_tab, width=200)
        left_frame.pack(side="left", fill="y")

        # Add checkboxes for each action
        self.actions = [
            ("1. File Cleaning", self.file_cleaning),
            ("2. Insert IEs", self.insert_ies),
            ("3. Finish Bib Records and Delete Files", self.finish_bibs_clean_and_delete_files),
            ("4. Delete Finished Episodes From DB", self.delete_done_from_db),
            ("5. Update DB From Spreadsheet", self.update_db_from_spreadsheet),
            ("6. Create Records", self.create_records),
            ("7. Make SIPs", self.sip_routine),
            ("8. Harvest New Episodes", self.run_harvest),
        ]

        self.action_vars = []

        for i, (action_name, action_func) in enumerate(self.actions):
            if action_name == "7. Make SIPs":
                # Create a frame for the "Make SIPs" checkbox and the red note
                sip_frame = tk.Frame(left_frame)
                sip_frame.pack(anchor="w", pady=5)

                # Add the checkbox for "Make SIPs" within the sip_frame
                var = tk.BooleanVar()
                chk = tk.Checkbutton(sip_frame, text=action_name, variable=var, font=("Helvetica", 10), anchor="w")
                chk.pack(side="left")
                self.action_vars.append(var)

                # Add red text next to the "Make SIPs" checkbox within the sip_frame
                sip_warning_label = tk.Label(sip_frame, text="Use option 7 only with options 2 and 3 from Thurs to Mon", font=("Helvetica", 10), fg="red")
                sip_warning_label.pack(side="left", padx=5)

                # Add an info button next to the warning label
                info_button = tk.Button(sip_frame, text="i", font=("Helvetica", 10, "bold"), fg="blue", command=self.show_sip_info)
                info_button.pack(side="left")

                # Link the "Make SIPs" checkbox to the "Insert IEs" checkbox
                var.trace_add("write", self.auto_check_insert_ies)
            else:
                var = tk.BooleanVar()
                chk = tk.Checkbutton(left_frame, text=action_name, variable=var, font=("Helvetica", 10), anchor="w")
                chk.pack(pady=5, anchor="w")
                self.action_vars.append(var)




        # Link the "Make SIPs" checkbox to the "Insert IEs" checkbox
        self.action_vars[6].trace_add("write", self.auto_check_insert_ies)

        # Run button to execute selected actions
        run_btn = tk.Button(left_frame, text="Run Actions", command=self.run_selected_actions, font=("Helvetica", 10))
        run_btn.pack(pady=10, anchor="w")

        # Add a label for the queries section
        query_label = tk.Label(left_frame, text="Queries", font=("Helvetica", 12))
        query_label.pack(pady=(20, 5), anchor="w")

        # Add checkboxes for each query
        self.queries = [
            ("1. Export DB to CSV", export_data_to_csv),
            ("2. Check last issue before date", find_podcast_with_last_episode_harvested_before_date),
            ("3. Find episodes by pattern", find_episode_by_pattern),
            ("4. Insert episodes to DB from spreadsheet", self.read_from_gs_to_db),
            ("5. Delete episodes and files from DB", delete_episode_by_id),
        ]

        self.query_vars = []
        query_frame = tk.Frame(left_frame)
        query_frame.pack(pady=5, anchor="w")

        for i, (query_name, _) in enumerate(self.queries):
            var = tk.BooleanVar()
            chk = tk.Checkbutton(query_frame, text=query_name, variable=var, font=("Helvetica", 10), anchor="w")
            chk.grid(row=i, column=0, pady=5, sticky="w")
            self.query_vars.append(var)

            if i == 0:  # Add the Entry widget next to Query 1 for CSV path
                query1_path_label = tk.Label(query_frame, text="Path:", font=("Helvetica", 10))
                query1_path_label.grid(row=i, column=1, padx=5, sticky="w")
                self.csv_path_entry = tk.Entry(query_frame, width=30)
                self.csv_path_entry.grid(row=i, column=2, padx=5, sticky="w")
                path_browse_btn = tk.Button(query_frame, text="Browse", command=self.browse_csv_path)
                path_browse_btn.grid(row=i, column=3, padx=5, sticky="w")

            if i == 1:  # Add the DateEntry widget next to Query 2
                query2_date_label = tk.Label(query_frame, text="Date:", font=("Helvetica", 10))
                query2_date_label.grid(row=i, column=1, padx=5, sticky="w")
                self.query2_date = tkc.DateEntry(query_frame, date_pattern="dd/mm/yyyy")
                self.query2_date.grid(row=i, column=2, padx=5, sticky="w")

            if i == 2:  # Add the Entry widget next to Query 3
                query3_pattern_label = tk.Label(query_frame, text="Pattern:", font=("Helvetica", 10))
                query3_pattern_label.grid(row=i, column=1, padx=5, sticky="w")
                self.pattern_entry = tk.Entry(query_frame)
                self.pattern_entry.grid(row=i, column=2, padx=5, sticky="w")
            if i == 3:  # Add the Entry widgets next to Query 4
                self.start_label = tk.Label(query_frame, text="Start row:", font=("Helvetica", 10))
                self.start_label.grid(row=i, column=1, padx=5, sticky="w")

                self.start_entry = tk.Entry(query_frame)
                self.start_entry.grid(row=i, column=2, padx=5, sticky="w")

                self.end_label = tk.Label(query_frame, text="End row:", font=("Helvetica", 10))
                self.end_label.grid(row=i, column=3, padx=5, sticky="w")

                self.end_entry = tk.Entry(query_frame)
                self.end_entry.grid(row=i, column=4, padx=5, sticky="w")
            if i == 4:
                query4_pattern_label = tk.Label(query_frame, text="Episode ID", font=("Helvetica", 10))
                query4_pattern_label.grid(row=i, column=1, padx=5, sticky="w")
                self.id_entry = tk.Entry(query_frame)
                self.id_entry.grid(row=i, column=2, padx=5, sticky="w")


        # Run button to execute selected queries
        run_queries_btn = tk.Button(left_frame, text="Run Queries", command=self.run_selected_queries, font=("Helvetica", 10))
        run_queries_btn.pack(pady=10, anchor="w")


    def auto_check_insert_ies(self, *args):
            # Automatically check "Insert IEs" when "Make SIPs" is checked
            if self.action_vars[6].get():
                self.action_vars[1].set(True)
                self.action_vars[2].set(True)


    def create_cleaning_tab(self):


        # Left frame for cleaning scripts
        left_frame = tk.Frame(self.cleaning_tab, width=400)
        left_frame.pack(side="left", fill="y")

        # Option 1: "Select cleaning report folder"
        option1_frame = tk.Frame(left_frame)
        option1_frame.pack(anchor="w", pady=5)

        # Separate BooleanVar for the first checkbox
        self.option1_var = tk.BooleanVar()
        option1_chk = tk.Checkbutton(option1_frame, text="1. Select cleaning report folder", variable=self.option1_var, font=("Helvetica", 10), anchor="w")
        option1_chk.grid(row=0, column=0, sticky="w")
        self.report_folder_entry = tk.Entry(option1_frame, width=20)  
        self.report_folder_entry.grid(row=0, column=1, padx=(10, 5), sticky="w")
        browse_report_btn = tk.Button(option1_frame, text="Browse", command=self.browse_cleaning_report_folder)
        browse_report_btn.grid(row=0, column=2, padx=5, sticky="w")
        report_warning_label = tk.Label(option1_frame, text="Always select.", font=("Helvetica", 10), fg="red")
        report_warning_label.grid(row=1, column=0, columnspan=3, sticky="w", padx=5)  


        # Divider after option 1
        divider = tk.Frame(left_frame, height=2, bd=1, relief=tk.SUNKEN)
        divider.pack(fill="x", padx=5, pady=10)

        # Option 2: "Browse results csv and build json file"
        option2_frame = tk.Frame(left_frame)
        option2_frame.pack(anchor="w", pady=5)

        # Separate BooleanVar for the second checkbox
        self.option2_var = tk.BooleanVar()
        option2_chk = tk.Checkbutton(option2_frame, text="2. Browse results csv and build json file", variable=self.option2_var, font=("Helvetica", 10), anchor="w")
        option2_chk.grid(row=0, column=0, sticky="w")
        self.sprsh_path_entry = tk.Entry(option2_frame, width=20)  # Adjusted width
        self.sprsh_path_entry.grid(row=0, column=1, padx=(10, 5), sticky="w")
        browse_csv_btn = tk.Button(option2_frame, text="Browse", command=self.browse_result_spreadsheet)
        browse_csv_btn.grid(row=0, column=2, padx=5, sticky="w")
        self.cleaning_var = tk.IntVar()
        self.cleaning_checkbox = tk.Checkbutton(option2_frame, text="Clear", variable=self.cleaning_var)
        self.cleaning_checkbox.grid(row=0, column=3, padx=5, sticky="w")


        # Additional entry fields for columns (Series, Title, MMS ID)
        series_label = tk.Label(option2_frame, text="Series Column:", font=("Helvetica", 10))
        series_label.grid(row=1, column=0, padx=5, sticky="w")
        self.series_entry = tk.Entry(option2_frame, width=7)  # Length 7
        self.series_entry.insert(0, "D")  # Initial value "D"
        self.series_entry.grid(row=1, column=1, padx=(10, 5), sticky="w")

        title_label = tk.Label(option2_frame, text="Title Column:", font=("Helvetica", 10))
        title_label.grid(row=2, column=0, padx=5, sticky="w")
        self.title_entry = tk.Entry(option2_frame, width=7)  # Length 7
        self.title_entry.insert(0, "E")  # Initial value "E"
        self.title_entry.grid(row=2, column=1, padx=(10, 5), sticky="w")

        mms_id_label = tk.Label(option2_frame, text="MMS ID Column:", font=("Helvetica", 10))
        mms_id_label.grid(row=3, column=0, padx=5, sticky="w")
        self.mms_id_entry = tk.Entry(option2_frame, width=7)  # Length 7
        self.mms_id_entry.insert(0, "AB")  # Initial value "27"
        self.mms_id_entry.grid(row=3, column=1, padx=(10, 5), sticky="w")


        option2_warning_label = tk.Label(option2_frame, text="Run it separately overnight. It takes 16 hours to make json file.", font=("Helvetica", 10), fg="red")
        option2_warning_label.grid(row=4, column=0, columnspan=4, sticky="w", padx=5)

        # Divider after option 2
        divider = tk.Frame(left_frame, height=2, bd=1, relief=tk.SUNKEN)
        divider.pack(fill="x", padx=5, pady=10)

        # Add checkboxes and entries for remaining options
        self.cleaning = [
            ("3. Pick up json file", self.browse_json_file),
            ("4. Check for double items and representations", pc.check_for_double_item_rep),
            ("5. Check for missing items, holdings, representations", pc.check_for_no_items_rep),
            ("6. Clean json from good records", pc.clean_dictionary_from_good_records),
            ("7. Delete bibs by mms when one good and others empty", pc.delete_mms_with_one_good_and_others_empty),
            ("8. RSS report in Excel spreadsheet", pc.make_spreadsheet)

        ]

        self.cleaning_vars = []
        for i, (query_name, command) in enumerate(self.cleaning):
            option_frame = tk.Frame(left_frame)
            option_frame.pack(anchor="w", pady=5)

            var = tk.BooleanVar()
            chk = tk.Checkbutton(option_frame, text=query_name, variable=var, font=("Helvetica", 10), anchor="w")
            chk.grid(row=0, column=0, sticky="w")
            self.cleaning_vars.append(var)

            if i == 0:  # Option 3: Pick up JSON file
                self.json_path_entry = tk.Entry(option_frame, width=20)  # Adjusted width
                self.json_path_entry.grid(row=0, column=1, padx=(10, 5), sticky="w")
                browse_json_btn = tk.Button(option_frame, text="Browse", command=command)
                browse_json_btn.grid(row=0, column=2, padx=5, sticky="w")
                option2_warning_label = tk.Label(option_frame, text="Pick up  main json file. Please use possible dups for the option 7.", font=("Helvetica", 10), fg="red")
                option2_warning_label.grid(row=1, column=0, columnspan=3, sticky="w", padx=5)

            if i == 4:  # Option 7: Delete bibs by mms...
                option7_warning_label = tk.Label(option_frame, text="Please run it separately and pick up possible dups json file.\n (It appears after running option 6)", font=("Helvetica", 10), fg="red")
                option7_warning_label.grid(row=1, column=0, columnspan=3, sticky="w", padx=5)

        # Run button to execute selected cleaning scripts
        run_cleaning_btn = tk.Button(left_frame, text="Run Cleaning Scripts", command=self.run_selected_cleaning, font=("Helvetica", 10))
        run_cleaning_btn.pack(pady=10, anchor="w")

     # Add a button to clear the log text box
        clear_cleaning_log_btn = tk.Button(left_frame, text="Clear Log", command=self.clear_cleaning_log, font=("Helvetica", 10))
        clear_cleaning_log_btn.pack(pady=2, anchor="w")

        # Right frame for image and progress log
        right_frame = tk.Frame(self.cleaning_tab)
        right_frame.pack(side="right", fill="both", expand=True)

        # Upper part: display PNG image
        image_frame = tk.Frame(right_frame)
        image_frame.pack(side="top", fill="both")

        self.load_image(image_frame,cleaning_scheme_path)

        # Lower part: display progress log
        log_frame = tk.Frame(right_frame, borderwidth=2, relief="sunken")
        log_frame.pack(side="bottom", expand=True, fill="both")

        log_label = tk.Label(log_frame, text="Cleaning Log", font=("Helvetica", 12))
        log_label.pack(pady=5)

        self.cleaning_log = scrolledtext.ScrolledText(log_frame, wrap="word", height=15)
        self.cleaning_log.pack(expand=True, fill="both")



    def create_documentation_tab(self, documentation_tab):
        # Create a frame inside the documentation tab
        doc_frame = tk.Frame(documentation_tab)
        doc_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Add a label to display the documentation link
        doc_link_label = tk.Label(doc_frame, text="Documentation Link:", font=("Helvetica", 12))
        doc_link_label.pack(anchor="w", pady=(0, 5))

        # Add an entry widget to display the link and allow selection
        self.doc_link_entry = tk.Entry(doc_frame, width=60, font=("Helvetica", 10))
        self.doc_link_entry.insert(0, "https://github.com/nlnzcollservices/podcast-collector/tree/master/documentation")
        self.doc_link_entry.config(state="readonly")  # Make the entry read-only
        self.doc_link_entry.pack(anchor="w", fill="x", pady=(0, 10))

        # Add a button to copy the link to the clipboard
        copy_button = tk.Button(doc_frame, text="Copy Link", command=self.copy_doc_link, font=("Helvetica", 10))
        copy_button.pack(anchor="w", pady=(0, 10))

        # Add a HTMLLabel to view the GitHub page
        html_view = HTMLLabel(doc_frame, html=f'<a href="https://github.com/nlnzcollservices/podcast-collector/tree/master/documentation">View Documentation on GitHub</a>')
        html_view.pack(expand=True, fill="both")

        # You can directly display some HTML content or a message to the user
        html_view.fit_height()



    def copy_doc_link(self):
        """Copy the documentation link to the clipboard."""
        self.clipboard_clear()
        self.clipboard_append(self.doc_link_entry.get())
        self.update()  # Now it stays on the clipboard after the window is closed
        messagebox.showinfo("Link Copied", "The documentation link has been copied to the clipboard.")



###################################################Appearence additional scripts###############################################################################



    def show_sip_info(self):
        messagebox.showinfo("Make SIPs Information", 
            "The current SIP structure - 'Serial MMS ID --> MIS MMS ID' requires a logic, which first should remove the old SIPs, "
            "then delete 'done' files from SIPs in Rosetta folder and only after that place new SIPs named as MIS MMS ID "
            "to folder named as Serial MMS ID. 'Done' file is a flag for Rosetta, indicating that it should not process this SIP again. "
            "If the folder is not empty from the last ingest and 'done' file is removed, Rosetta will process the SIPs again which will lead to duplication. "
            "Or opposite, the script will not remove 'done' file and the new SIP will be stuck unprocessed."
            "Please use this option in the time frame from Thursday to Monday, which is outside of Rosetta scheduled jobs, which are early Tues and early Thurs each week. ")

    def clear_log(self):
        self.log_text.delete("1.0", tk.END)

    def clear_cleaning_log(self):
        self.cleaning_log.delete("1.0", tk.END)

            
    def create_log_textbox(self):

        # Right frame for image and progress log
        right_frame = tk.Frame(self.actions_tab)
        right_frame.pack(side="right", expand=True, fill="both")

        # Upper part: display PNG image
        image_frame = tk.Frame(right_frame)
        image_frame.pack(side="top", fill="both")

        self.load_image(image_frame)

        # Lower part: display progress log
        log_frame = tk.Frame(right_frame, borderwidth=2, relief="sunken")
        log_frame.pack(side="bottom", expand=True, fill="both")

        log_label = tk.Label(log_frame, text="Progress Log", font=("Helvetica", 14))
        log_label.pack(pady=5)

                # Add a button to clear the log text box
        clear_log_btn = tk.Button(log_frame, text="Clear Log", command=self.clear_log, font=("Helvetica", 10))
        clear_log_btn.pack(side="right", anchor="w", pady=2)

        self.log_text = tk.Text(log_frame, wrap="word", height=15)
        self.log_text.pack(expand=True, fill="both")



    def load_image(self, frame, path=scheme_path):
        try:
            image = Image.open(path)
            # Use Resampling.LANCZOS for anti-aliasing during resize
            image = image.resize((self.winfo_screenwidth() // 3, self.winfo_screenheight() // 3), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(image)

            label = tk.Label(frame, image=self.photo)
            label.image = self.photo  # Keep a reference to avoid garbage collection
            label.pack(expand=True, fill="both")

            # Bind left mouse click to open the image in a new window
            label.bind("<Button-1>", lambda event, p=path: self.open_fullscreen_image(event, p))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

    def open_fullscreen_image(self, event, path=scheme_path):
        new_window = tk.Toplevel(self)
        new_window.attributes("-fullscreen", True)
        new_window.bind("<Escape>", lambda e: new_window.destroy())  # Close the fullscreen window on pressing Esc

        try:
            full_image = Image.open(path)
            full_photo = ImageTk.PhotoImage(full_image)

            # Create a canvas and add scrollbars
            canvas = tk.Canvas(new_window)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            scrollbar_y = tk.Scrollbar(new_window, orient=tk.VERTICAL, command=canvas.yview)
            scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

            scrollbar_x = tk.Scrollbar(new_window, orient=tk.HORIZONTAL, command=canvas.xview)
            scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
            canvas.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
            
            # Add the image to the canvas
            canvas.create_image(0, 0, image=full_photo, anchor="nw")
            canvas.image = full_photo  # Keep a reference to avoid garbage collection

            # Configure the scroll region
            canvas.config(scrollregion=canvas.bbox(tk.ALL))

            # Add a close button
            close_button = tk.Button(new_window, text="Close", command=new_window.destroy)
            close_button.pack(anchor="ne")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load full-screen image: {e}")

####################################################Selected options runners#####################################################################################


    def run_selected_actions(self):

        try:
            # copy the database file
            shutil.copyfile(database_fullname, os.path.join(database_archived_folder, "podcasts_{}.db".format(dt.now().strftime("%Y-%m-%d_%H"))))
            self.db_handler = DbHandler()
            self.log_text.insert(tk.END, "Database backup and initialization completed.\n")
        except Exception as e:
            self.log_text.insert(tk.END, f"Error during database backup: {e}\n")

        for var, (_, action_func) in zip(self.action_vars, self.actions):
            if var.get():
                action_func()


    def run_selected_queries(self):
        for index, (var, (_, query_func)) in enumerate(zip(self.query_vars, self.queries)):
            if var.get():
                if index == 0:

                    self.log_text.insert(tk.END, f"Query {index + 1} executed.\n")
                    csv_path = self.csv_path_entry.get()
                    export_data_to_csv(os.path.join(csv_path,"complete_podcasts_data.csv"))
                    self.log_text.insert(tk.END, f"DB exported to csv.\n")

                elif index == 1:

                    my_date = self.query2_date.get_date().strftime("%d/%m/%Y")
                    self.log_text.insert(tk.END, f"Query {index + 1} executed with date {my_date}.\n")
                    result = find_podcast_with_last_episode_harvested_before_date(my_date)
                    self.log_text.insert(tk.END, result)
                    self.log_text.insert(tk.END, f"Done.\n")

                elif index == 2:  

                    self.log_text.insert(tk.END, f"Query {index + 1} executed.\n")
                    pattern = self.pattern_entry.get()
                    result = find_episode_by_pattern(pattern)
                    self.log_text.insert(tk.END, result)
                    self.log_text.insert(tk.END, f"Done.\n")

                elif index == 3:  

                    self.log_text.insert(tk.END, f"Query {index + 1} executed.\n")
                    start = self.start_entry.get()
                    end = self.end_entry.get()
                    self.read_from_gs_to_db(start,end)
                    self.log_text.insert(tk.END, f"Done.\n")

                elif index == 4:

                    self.log_text.insert(tk.END, f"Query {index + 1} executed.\n")
                    episode_id = self.id_entry.get()
                    result = delete_episode_by_id(episode_id)
                    self.log_text.insert(tk.END, result+"\n")
                    self.log_text.insert(tk.END, f"Done.\n")

    def run_selected_cleaning(self):

        try:
            # Check if option 1 (Select cleaning report folder) is selected
            if self.option1_var.get():
                self.cleaning_log.insert(tk.END, "Running: Select cleaning report folder\n")
                result_path = self.report_folder_entry.get()
                self.cleaning_log.insert(tk.END, f"Report folder selected: {result_path}\n")

            # Check if option 2 (Browse results csv and build json file) is selected
            if self.option2_var.get():
                self.cleaning_log.insert(tk.END, "Running: Browse results csv and build json file\n")
                series_idx = self.column_name_to_index(self.series_entry.get())
                title_idx = self.column_name_to_index(self.title_entry.get())
                mms_idx = self.column_name_to_index(self.mms_id_entry.get())
                sprsheet_path = self.sprsh_path_entry.get()
                clear = self.cleaning_var.get()
                cp = PodcastCleaningPipeline(result_path)
                cp.parse_spreadsheet(sprsheet_path, clear, mms_idx, series_idx, title_idx)
                self.cleaning_log.insert(tk.END, "JSON created.\n")

            # Loop through the other cleaning options
            for i, (var, (_, query_func)) in enumerate(zip(self.cleaning_vars, self.cleaning)):
                if var.get():
                    self.cleaning_log.insert(tk.END, f"Running: {query_func.__name__}\n")
                    if i == 0:  # Pick up JSON file
                        self.json_file_path = self.json_path_entry.get()
                        self.cleaning_log.insert(tk.END, "JSON file selected.\n")

                    elif i == 1:  

                        self.cleaning_log.insert(tk.END, f"Checking for duplicates.\n")
                        cp = PodcastCleaningPipeline(result_path)
                        result = cp.check_for_double_item_rep(self.json_file_path)
                        self.cleaning_log.config(state=tk.NORMAL)
                        self.cleaning_log.insert(tk.END, result)
                        self.log_text.insert(tk.END, "Done.\n")

                    elif i == 2:  

                        self.log_text.insert(tk.END, f"Checking for missing items and reps.\n")
                        cp = PodcastCleaningPipeline(result_path)
                        result = cp.check_for_no_items_rep(self.json_file_path)
                        self.cleaning_log.config(state=tk.NORMAL)
                        self.cleaning_log.insert(tk.END, result)
                        self.log_text.insert(tk.END, "Done.\n")

                    elif i == 3:

                        self.log_text.insert(tk.END, f"Making json with problematic bibs.\n")
                        cp = PodcastCleaningPipeline(result_path)
                        result = cp.clean_dictionary_from_good_records(self.json_file_path)
                        self.cleaning_log.config(state=tk.NORMAL)
                        self.cleaning_log.insert(tk.END, result)
                        self.log_text.insert(tk.END, "Done.\n")

                    elif i == 4:

                        self.log_text.insert(tk.END, f"Deleting empty bib records when full exists. \n")
                        cp = PodcastCleaningPipeline(result_path)
                        result = cp.delete_mms_with_one_good_and_others_empty(self.json_file_path)
                        self.cleaning_log.config(state=tk.NORMAL)
                        self.cleaning_log.insert(tk.END, result)
                        self.log_text.insert(tk.END, "Done.\n")

                    elif i == 5:

                        self.log_text.insert(tk.END, f"Make rss report in xlsx format. \n")
                        cp = PodcastCleaningPipeline(result_path)
                        result = cp.make_spreadsheet(self.json_file_path)
                        self.cleaning_log.config(state=tk.NORMAL)
                        self.cleaning_log.insert(tk.END, result)
                        self.log_text.insert(tk.END, "Done.\n")



        except Exception as e:
            self.cleaning_log.insert(tk.END, f"Error: {str(e)}\n")

############################################################   Podcasts main pipeline ################################################################################### 


    def file_cleaning(self):
        
        """This function activates file cleaning for podcast pipeline to delete all files which are not in db"""
        my_pipeline = Podcast_pipeline(self.key)
        my_pipeline.db_handler = DbHandler()
        if self.action_vars[0].get():  # Check if the File Cleaning checkbox is ticked
            try:
                my_pipeline.file_cleaning()  # Call the file_cleaning method from FPodcast_pipeline
                self.log_text.insert(tk.END, "File cleaning executed.\n")
            except Exception as e:
                self.log_text.insert(tk.END, f"Error during file cleaning: {e}\n")
        else:
            self.log_text.insert(tk.END, "File cleaning not selected.\n")


    def insert_ies(self):

        """This funcion activates mechanism which is inserting IEs to db"""
        try:
            db_handler = DbHandler()
            my_pipeline = Podcast_pipeline(self.key)
            my_pipeline.db_handler = DbHandler()
            my_pipeline.insert_ies()
            self.log_text.insert(tk.END, f"Insert IEs completed successfully.\n")
        except Exception as e:
            self.log_text.insert(tk.END,f"Error during Insert IEs: {e} \n")


    def finish_bibs_clean_and_delete_files(self):

        """This function accivates podcast pipeline mechanisms which are adding 942 to bib records and delete files from files, project SIP folder and Rosetta folder"""
        try:
            db_handler = DbHandler()
            my_pipeline = Podcast_pipeline(self.key)
            my_pipeline.db_handler = db_handler
            print(self.key)
            my_pipeline.finish_existing_records_and_delete_files(self.key)
            self.log_text.insert(tk.END,f"Finished bib records, cleaned items and deleted audio files.\n")
        except Exception as e:
            self.log_text.insert(tk.END,f"Error during finish and delete records: {e}\n")


    def delete_done_from_db(self):

        """This function activates machanisms which are cleaning db from done episodes"""

        try:
            db_handler = DbHandler()
            db_handler.delete_done_from_db()
            self.log_text.insert(tk.END,f"Deleted finished items from DB completed successfully.\n")
        except Exception as e:
            self.log_text.insert(tk.END,f"Error during deleting done episodes from database: {e}\n")

    def update_db_from_spreadsheet(self):

        """This function activates mechanism in the pipeline which updates db from spreadsheet"""

        try:
            db_handler = DbHandler()
            my_pipeline = Podcast_pipeline(self.key)
            my_pipeline.db_handler = db_handler
            print(self.key)
            my_pipeline.update_database_from_spreadsheetand_delete_row()
            self.log_text.insert(tk.END, "Successfully updated database from spreadsheet.\n")
        except Exception as e:
            self.log_text.insert(tk.END,f"Error during updating database from spreadsheet: {e}\n")

    def create_records(self): 

        """This function activates bib records creating mechanism in  the podcasts pipeline"""

        try:
            my_rec = RecordCreator(self.key)
            my_rec.record_creating_routine()
            self.log_text.insert(tk.END, "Records were created.\n")
        except Exception as e:
            self.log_text.insert(tk.END,f"Error during created records: {e}\n")


    def sip_routine(self):

        """This function activates sip building mechanism in the podcasts pipeline"""

        try:
            sip_routine()
            self.log_text.insert(tk.END, "SIPs created successfully.\n")
        except Exception as e:
            self.log_text.insert(tk.END,f"Error during making SIPs: {e}\n")

    def run_harvest(self):

        """This function activates the podcasts harvester"""

        try:
            harvest()
            self.log_text.insert(tk.END, "New episodes harvested.\n")
            db_handler = DbHandler()
            db_handler.update_the_last_issue()
            self.log_text.insert(tk.END, "Last episode dates updated.\n")
        except Exception as e:
            self.log_text.insert(tk.END,f"Error during harvesting: {e}\n")

#########################################################Query scripts#######################################################################################

    

    def browse_csv_path(self):

        """This script browses and set path for csv  for exproted from db  podcast episodes data"""

        file_path = filedialog.askdirectory()
        if file_path:
            self.csv_path_entry.delete(0, tk.END)
            self.csv_path_entry.insert(0, file_path)


    def read_from_gs_to_db(self, start_row, end_row):

        """This script activates spreadsheet reading query script

        Parametets:
            start_row (str) - number of start row
            end_row (str) - number of end row

        """

        try:
            sprshreader = ReadFromSpreadsheet(start_row, end_row)
            episode_titles= sprshreader.get_metadata_from_row()
            for ep_tit in episode_titles:
                print(ep_tit)
                self.log_text.insert(tk.END, str(ep_tit)+"\n")
            self.log_text.insert(tk.END, "Inserted successfully to db.\n")
        except Exception as e:
            self.log_text.insert(tk.END,f"Error during inserting to db: {e}\n")




#########################################################Cleaning scriptis###################################################################################33

    
    def browse_cleaning_report_folder(self):


        """This function sets cleaning folder in the given path. The folder will be called "Cleaning report_month_year" """

        file_path = filedialog.askdirectory()
        if file_path:
            self.report_folder_entry.delete(0, tk.END)
            self.report_folder_entry.insert(0, file_path)
            self.cleaning_log.config(state='normal')
            self.cleaning_log.insert(tk.END, f"Selected folder: {file_path}\n")



    def browse_result_spreadsheet(self):

        """This function select results.csv file which exported from Alma set with all podcasts"""

        filename = filedialog.askopenfilename()
        if filename:
            self.sprsh_path_entry.delete(0, tk.END)  # Clear the Entry widget
            self.sprsh_path_entry.insert(0, filename)  # Set the selected file path in the Entry widget
            self.cleaning_log.config(state='normal')
            self.cleaning_log.insert(tk.END, f"Selected file: {filename}\n")


    def column_name_to_index(self, column_name):
        """
        Convert an Excel column name to a zero-based column index.
        
        Args:
        column_name (str): The column name (e.g., "A", "B", "AA").
        
        Returns:
        int: The zero-based column index.
        """
        column_name = column_name.upper()  # Ensure the column name is uppercase
        index = 0
        for char in column_name:
            index = index * 26 + (ord(char) - ord('A') + 1)
        return index - 1  # Convert to zero-based index


    def browse_json_file(self):

        """This function selects json file, which is product of spreadsheet parsing and requests to Alma API"""

        filename = filedialog.askopenfilename()
        if filename:
            self.json_path_entry.delete(0, tk.END)  # Clear the Entry widget
            self.json_path_entry.insert(0, filename)  # Set the selected file path in the Entry widget
            self.cleaning_log.config(state='normal')
            self.cleaning_log.insert(tk.END, f"Selected file: {filename}\n")



                 
   
    def run_rss_report(self):
        # Placeholder for running RSS report script
        pass




if __name__ == "__main__":
    app = PodcastPipelineGUI()
    app.mainloop()
