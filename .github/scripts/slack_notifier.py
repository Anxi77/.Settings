import os
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime
import pytz

def format_task_message(issue_data, event_type):
    """태스크 관련 Slack 메시지 포맷팅"""
    title = issue_data['title']
    url = issue_data['html_url']
    user = issue_data['user']['login']
    
    if event_type == 'opened':
        header = "🆕 새로운 태스크가 제안되었습니다"
    elif 'labeled' in event_type:
        labels = [label['name'] for label in issue_data['labels']]
        if '✅ 승인완료' in labels:
            header = "✅ 태스크가 승인되었습니다"
        elif '❌ 반려' in labels:
            header = "❌ 태스크가 반려되었습니다"
        elif '⏸️ 보류' in labels:
            header = "⏸️ 태스크가 보류되었습니다"
        else:
            header = "🏷 태스크 라벨이 업데이트되었습니다"
    elif event_type == 'closed':
        header = "🎉 태스크가 완료되었습니다"
    else:
        header = "ℹ️ 태스크가 업데이트되었습니다"
    
    return {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": header
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*제목:*\n{title}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*작성자:*\n{user}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"👉 <{url}|이슈 보러가기>"
                }
            },
            {
                "type": "divider"
            }
        ]
    }

def format_daily_log_message(issue_data):
    """일일 개발 로그 Slack 메시지 포맷팅"""
    title = issue_data['title']
    url = issue_data['html_url']
    
    return {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📅 새로운 일일 개발 로그가 생성되었습니다"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{title}*\n\n👉 <{url}|로그 보러가기>"
                }
            },
            {
                "type": "divider"
            }
        ]
    }

def send_slack_notification(message):
    """Slack으로 메시지 전송"""
    client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
    channel_id = os.environ['SLACK_CHANNEL_ID']
    
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            blocks=message['blocks']
        )
        print(f"메시지 전송 성공: {response['ts']}")
    except SlackApiError as e:
        print(f"에러 발생: {e.response['error']}")

def main():
    # GitHub 이벤트 정보 읽기
    event_path = os.environ['GITHUB_EVENT_PATH']
    event_name = os.environ['GITHUB_EVENT_NAME']
    
    with open(event_path, 'r', encoding='utf-8') as f:
        event_data = json.load(f)
    
    # 이슈 데이터 가져오기
    issue_data = event_data['issue']
    
    # 메시지 포맷팅
    if '📅 Daily Development Log' in issue_data['title']:
        message = format_daily_log_message(issue_data)
    else:
        message = format_task_message(issue_data, event_name)
    
    # Slack으로 전송
    send_slack_notification(message)

if __name__ == '__main__':
    main() 