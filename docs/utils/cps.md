## Use the Annotator in CPS

### Build a Model

For invoking the annotator from CPS, make sure of the following:
1. The API is running (see above) and is reachable from the CPS instance.
     * For development, you could use ngrok, see section below.
2. Create a Model in CPS and give it a name. (In the screenshot below it's "external-ngrok".)
3. Choose Type `ExternalApiAnnotator`.
4. Add a header with key `Authorization` and set its Value to the `Api Key` from your `config.json`.
4. As URL, provide the endpoint of your API, for example: 
    * http://localhost:5000/api/v1/annotators/SimpleTextGeographyAnnotator if you have a local CPS instance, 
    * else the same with your ngrok address instead of `localhost:5000`.

![cps](.readme_resources/cps.png)

CPS will validate the configuration discovery of your annotator and confirm that the model is correct. If yes, the UI will show the list of entities and relationships declared by your annotator.

### Use the Model
You can then try the new model in the "Preview" field, and use it in a CPS dataflow.

You can use the annotator on text and tables.


## Using an Ngrok Tunnel

After running and testing the application locally, you can create a tunnel with ngrok to expose it to test in CPS by creating an external API model.

### Create an account at Ngrok

1. Access https://ngrok.com and go into signup (if you don't have an account yet).
   ![ngrok1](.readme_resources/ngrok1.png)
2. Fill with your information (email, name, password)
   ![ngrok2](.readme_resources/ngrok5.png)

### Install ngrok tool

1. Download the .zip from the get started page of the dashboard at https://dashboard.ngrok.com/get-started/setup
2. Extract the ngrok tool.
3. In the repository where you put ngrok, run `./ngrok authtoken {token}` with the token provided in the get started screen:
   ![ngrok3](.readme_resources/ngrok2.png)

### Use ngrok tool

1. Run `./ngrok http {PORT}` where `{PORT}` is the port that your local application is using (default 5000).
   ![ngrok4](.readme_resources/ngrok3.png)
2. The result will show the external URL to access:
   ![ngrok5](.readme_resources/ngrok4.png)


