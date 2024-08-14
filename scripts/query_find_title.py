import peewee
from podcast_models import Podcast, Episode, File
from datetime import datetime as dt



def find_episode_by_pattern(pattern):
    log = []

    podcasts = Podcast.select()


    for podcast in podcasts:
        episodes = Episode.select().where(Episode.podcast == podcast.id)
        
        # Iterate over episodes for each podcast
        for episode in episodes:
            # Example of checking a pattern in the episode title
            if pattern in episode.episode_title:
                files = File.select().where(File.episode == episode.id)
                formatted_date = dt.fromtimestamp(episode.date).strftime('%B %d %Y')
                
                # Iterate over files for each episode
                for fl in files:
                    # Append details to log list
                    log.append( "#"*50 + "\n"
                                f"Episode title: {episode.episode_title}. \n"
                                f"MMS ID: {episode.mis_mms}. \n"
                                f"Episode link: {episode.episode_link}.\n "
                                f"Harvest link: {episode.harvest_link}.\n "
                                f"File path: {fl.filepath}. \n"
                                f"Date: {formatted_date}.\n")
                    # Print details
                    print(log[-1])

    # Return the log list
    return log

if __name__ == '__main__':

  find_episode_by_pattern("test")