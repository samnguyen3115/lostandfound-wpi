#base image: 
FROM python:3.12.2-slim 
#set the home and working directory to be the app directory
ENV HOME=/app
ENV DATABASE_URL='postgresql+psycopg2://postgres:postgres@wpi-lostandfound.cf8c02si8b81.ap-southeast-2.rds.amazonaws.com/postgres'
WORKDIR /app

ENV CLIENT_SECRET="BNC8Q~PZLCyFCLfopE7l~Y3kf6QdG7ZAiNQ42dmN"
ENV CLIENT_ID="6dd22c70-603f-45a4-ac64-6183d9afd1d8"
ENV AUTHORITY="https://login.microsoftonline.com/589c76f5-ca15-41f9-884b-55ec15a0672a"
#move the requirements.txt text file into the container and install dependencies
ADD ./requirements.txt ./requirements.txt
RUN python -m venv venv
RUN /bin/bash -c "source ./venv/bin/activate"
RUN pip install --no-cache-dir -r requirements.txt 
#copy all files into the app directory (inside the container)
#install openssh
RUN apt-get update && apt-get install -y openssl
#generate a self-signed ssl certificate. This line creates a key for 365 days, using RSA encoding. 
#generates an ssl key and certificate for 365 days and saves them to known ssl-releated directories
#-nodes prevents encryption of the private key, -subj holds info for ssl certificate 
#note - when entering your ec2 ipv4 address, do not include either https or http. Should be something like ec2-3-145-113-82.us-east-2.compute.amazonaws.com (note that there is not an instance of http or https in this string)
RUN openssl req -x509 -newkey rsa:4096 -keyout /etc/ssl/private/key.pem -out /etc/ssl/certs/cert.pem -days 365 -nodes -subj "/C=US/ST=MA/L=Worcester/O=WPI/CN=[INSERT EC2 URL HERE]"
COPY . /app
#set flask to run the production environment
ENV FLASK_ENV=production
ENV PATH=/app/.local/bin:$PATH

#expose the port
EXPOSE 3001
# When deployed, run db upgrade then run the server on port 3001.
#TODO when you run the container map port 80 to 3001  
CMD ["sh", "-c", "flask db upgrade && flask run --host=0.0.0.0 --port=3001 --cert=/etc/ssl/certs/cert.pem --key=/etc/ssl/private/key.pem" ]
