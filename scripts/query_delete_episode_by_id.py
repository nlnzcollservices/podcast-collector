from podcasts_database_handler import DbHandler




def delete_episode_by_id(episode_id):
    try:
        db_handler = DbHandler()
        result = db_handler.db_delete_episodes_and_files_by_episode_id(episode_id)
        return f"Episode ID {episode_id} deleted successfully."
    except Exception as e:
        return f"Failed to delete episode ID {episode_id}: {e}"



if __name__ == '__main__':

	delete_episode_by_id(14384)