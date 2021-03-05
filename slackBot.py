import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
client = WebClient(
    token='')

# blockchain channel 에서 send message


def sendMessage(message):
    try:
        response = client.chat_postMessage(
            channel='#blockchain', text=message)
        assert response["message"]["text"] == message
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        # str like 'invalid_auth', 'channel_not_found'
        assert e.response["error"]
        print(f"Got an error: {e.response['error']}")


# message 작성
message = "[ENJKRW] UPBIT(500원 100개 매수) BINANCE(400원 100개 매도)"

# sendMessgae 실행
sendMessage(message)
