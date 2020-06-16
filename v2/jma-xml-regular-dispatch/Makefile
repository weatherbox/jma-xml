deploy:
	gcloud functions deploy jma-xml-regular-dispatch \
		--project=weatherbox-217409 \
		--region=asia-northeast1 \
		--trigger-topic=jma-xml-dispatch \
		--runtime=nodejs8 \
		--entry-point=handler
