from datetime import datetime


class htmlOperation():

    def __init__(self):
        pass

    def otp_verification_process(self, otp):
        try:
            otp_verification = """
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Quickoo - Your OTP Verification</title>
                    <style>
                        body {
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            margin: 0;
                            padding: 0;
                            background-color: #f5f5f5;
                        }
                        .container {
                            max-width: 600px;
                            margin: 0 auto;
                            padding: 20px;
                            background-color: #f2f2f2;
                            box-shadow: 1px 1px 5px #2c3e50;
                        }
                        .header {
                            text-align: center;
                            padding: 20px 0;
                            border-bottom: 1px solid #eeeeee;
                        }
                        .logo {
                            font-size: 32px;
                            font-weight: bold;
                            color: #2c3e50;
                        }
                        .logo span {
                            color: #e74c3c;
                        }
                        .content {
                            padding: 30px 20px;
                            color: #333333;
                        }
                        .otp-container {
                            margin: 30px 0;
                            text-align: center;
                        }
                        .otp-code {
                            font-size: 32px;
                            font-weight: bold;
                            letter-spacing: 8px;
                            padding: 15px 25px;
                            background-color: #f8f9fa;
                            border-radius: 8px;
                            color: #2c3e50;
                            display: inline-block;
                        }
                        .footer {
                            padding: 20px;
                            text-align: center;
                            font-size: 12px;
                            color: #777777;
                            border-top: 1px solid #eeeeee;
                        }
                        .social-icons {
                            margin: 15px 0;
                        }
                        .social-icon {
                            display: inline-block;
                            margin: 0 10px;
                            width: 30px;
                            height: 30px;
                            background-color: #2c3e50;
                            border-radius: 50%;
                            color: white;
                            line-height: 30px;
                            text-align: center;
                        }
                        .note {
                            padding: 15px;
                            background-color: #f8f9fa;
                            border-left: 4px solid #e74c3c;
                            margin: 20px 0;
                        }
                        @media only screen and (max-width: 600px) {
                            .container {
                                width: 100%;
                            }
                            .otp-code {
                                font-size: 24px;
                            }
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <div class="logo">Quick<span>oo</span></div>
                        </div>
                        <div class="content">
                            <h2>Verify Your Account</h2>
                            <p>Hello there,</p>
                            <p>Thank you for choosing Quickoo! Please use the verification code below to complete your account verification process:</p>

                            <div class="otp-container">
                                <div class="otp-code">""" + otp + """</div>
                            </div>

                            <p>This code will expire in <strong>10 minutes</strong>.</p>

                            <div class="note">
                                <p><strong>Security Note:</strong> If you didn't request this code, please ignore this email or contact our support team immediately.</p>
                            </div>

                            <p>If you have any questions or need assistance, our customer support team is always here to help.</p>

                            <p>Best Regards,<br>The Quickoo Team</p>
                        </div>
                        <div class="footer">
                            <p>&copy; 2025 Quickoo. All rights reserved.</p>
                            <p>This is an automated message, please do not reply to this email.</p>
                        </div>
                    </div>
                </body>
                </html>
                """

            return otp_verification

        except Exception as e:
            print(f"{datetime.now()}: Error in getting otp verification html format: {str(e)}")