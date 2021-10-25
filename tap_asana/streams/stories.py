
from singer import utils
from tap_asana.context import Context
from tap_asana.streams.base import Stream, asana_error_handling, REQUEST_TIMEOUT


@asana_error_handling
def get_stories_for_tasks(task_gid, opt_fields):
  stories = list(Context.asana.client.stories.get_stories_for_task(task_gid=task_gid,
                                                                   opt_fields=opt_fields,
                                                                   timeout=float(Context.config.get('request_timeout') or REQUEST_TIMEOUT)))
  return stories

class Stories(Stream):
  name = "stories"
  replication_key = "created_at"
  replication_method = 'INCREMENTAL'
  fields = [
    "gid",
    "resource_type",
    "created_at",
    "created_by",
    "resource_subtype",
    "text",
    "html_text",
    "is_pinned",
    "assignee",
    "dependency",
    "duplicate_of",
    "duplicated_from",
    "follower",
    "hearted",
    "hearts",
    "is_edited",
    "liked",
    "likes",
    "new_approval_status",
    "new_dates",
    "new_enum_value",
    "new_name",
    "new_number_value",
    "new_resource_subtype",
    "new_section",
    "new_text_value",
    "num_hearts",
    "num_likes",
    "old_approval_status",
    "old_dates",
    "old_enum_value",
    "old_name",
    "old_number_value",
    "old_resource_subtype",
    "old_section",
    "old_text_value",
    "preview",
    "project",
    "source",
    "story",
    "tag",
    "target",
    "task"
  ]


  def get_objects(self):
    bookmark = self.get_bookmark()
    session_bookmark = bookmark
    opt_fields = ",".join(self.fields)
    for workspace in self.call_api("workspaces"):
      for project in self.call_api("projects", workspace=workspace["gid"]):
        for task in self.call_api("tasks", project=project["gid"]): 
          task_gid = task.get('gid')
          for story in get_stories_for_tasks(task_gid, opt_fields):
            session_bookmark = self.get_updated_session_bookmark(session_bookmark, story[self.replication_key])
            if self.is_bookmark_old(story[self.replication_key]):
              yield story
    self.update_bookmark(session_bookmark)


Context.stream_objects['stories'] = Stories
