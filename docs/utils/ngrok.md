# Using an Ngrok Tunnel

After running and testing the application locally, you can create a tunnel with ngrok to expose it to test in CPS by creating an external API model.

## Create an account at Ngrok

1. Access https://ngrok.com and go into signup (if you don't have an account yet).
   ![ngrok1](.readme_resources/ngrok1.png)
2. Fill with your information (email, name, password)
   ![ngrok2](.readme_resources/ngrok5.png)

## Install ngrok tool

1. Download the .zip from the get started page of the dashboard at https://dashboard.ngrok.com/get-started/setup
2. Extract the ngrok tool.
3. In the repository where you put ngrok, run `./ngrok authtoken {token}` with the token provided in the get started screen:
   ![ngrok3](.readme_resources/ngrok2.png)

## Use ngrok tool

1. Run `./ngrok http {PORT}` where `{PORT}` is the port that your local application is using (default 5000).
   ![ngrok4](.readme_resources/ngrok3.png)
2. The result will show the external URL to access:
   ![ngrok5](.readme_resources/ngrok4.png)
