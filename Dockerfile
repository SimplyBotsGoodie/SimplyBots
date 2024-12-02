# Use the official Rasa Open Source image as the base
FROM rasa/rasa:3.6.20

# Set the working directory
WORKDIR /app

# Copy the Rasa project files
COPY . /app

# Switch to root user to fix permissions
USER root

# Fix permissions before installing dependencies
RUN chown -R root:root /opt/venv
RUN chmod -R 777 /opt/venv

# Install dependencies without the '--user' flag
RUN pip install --no-cache-dir -r requirements.txt

# Copy pre-trained model into the container
COPY models /app/models

# Expose the default Rasa server port
EXPOSE 5005

# Run the Rasa server
CMD ["run", "--enable-api", "--cors", "*", "--debug"]
