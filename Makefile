create-lambda-layer:
	mkdir -p $(FOLDER_NAME)
	pip3 install -t $(FOLDER_NAME)/python -r requirements.txt
	echo "Done"

zip-lambda-layer:
	@if [ -d $(FOLDER_NAME) ]; then \
		cd $(FOLDER_NAME) && zip -r $(FOLDER_NAME).zip . \
	else \
		echo "Folder does not exist" ; fi

publish-lambda-layer:
	@if [ -d $(FOLDER_NAME) ]; then \
		aws lambda publish-layer-version --layer-name $(FOLDER_NAME) --zip-file fileb://$(FOLDER_NAME)/$(FOLDER_NAME).zip --compatible-runtimes python3.8 --region $(REGION) > output.json; \
	else \
  		echo "Folder $(FOLDER_NAME) does not exist" ; fi

clean-up:
	@if [ -d $(FOLDER_NAME) ]; then \
		rm -r $(FOLDER_NAME) ; \
	else \
  		echo "Folder $(FOLDER_NAME) does not exist" ; \
 	fi

all: create-lambda-layer zip-lambda-layer publish-lambda-layer 
	@echo "Done"
