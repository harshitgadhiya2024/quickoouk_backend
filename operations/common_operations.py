from datetime import datetime

class commonOperation():


    def __init__(self):
        pass

    # get current utc timestamp
    def get_timestamp(self):
        try:
            current_datetime = datetime.utcnow()
            formatted_datetime = current_datetime.strftime("%m-%d-%Y %H:%M:%S")

            return formatted_datetime

        except Exception as e:
            print(f"{datetime.utcnow()}: Error when get timestamp: {e}")

    # get success response format
    def get_success_response(self, statuscode, data):
        try:
            response_data = {
                "data": data,
                "status": statuscode,
                "timestamp": commonOperation().get_timestamp()
            }

            return response_data

        except Exception as e:
            print(f"{datetime.utcnow()}: Error when format success response format: {e}")

    # get error response format
    def get_error_msg(self, error):
        try:
            response_data = {
                "data": {"message": error},
                "status": 403,
                "timestamp": commonOperation().get_timestamp()
            }

            return response_data

        except Exception as e:
            print(f"{datetime.utcnow()}: Error when got format for error response: {e}")

