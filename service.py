from utils import get_line_notify_token, get_all_file_path, parser_file, process_sent_notify
import setting

setting = setting.get_settings()


def sent_line_notify():
    # get all token list
    line_token_list = get_line_notify_token(setting.line_token_path)
    # get all file path in Sent folder
    files_path = get_all_file_path(setting.sent_file_path)
    # get all sent content list
    sent_content_list = parser_file(files_path)
    # sent LINE notify
    for content in sent_content_list:
        process_sent_notify(content, line_token_list)