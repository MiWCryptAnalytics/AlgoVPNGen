#!/bin/bash

function compress_and_display(){
	FILENAME=algo-configs-$(date +%Y%m%d)
	echo "--------------------------------------------"
	echo " Zipping configs"
	echo "--------------------------------------------"
	zip -r -9 $FILENAME.zip configs
	echo "-----ALGO CONFIG ZIP - START COPY BELOW-----"
	base64 $FILENAME.zip
	echo "-----ALGO CONFIG ZIP - END COPY ABOVE-----"
	echo ""
	echo "Copy the text from between the ALGO CONFIG ZIP sections. Save to a file named config.txt"
	echo ""
	echo "On linux/macos:"
	echo $" base64 -d configs.txt > configs.zip"
	echo "$ unzip configs.zip"
	echo ""
	echo "On windows:"
	echo ""
	echo "certutil -decode configs.txt configs.zip"
	echo "powershell.exe -nologo -noprofile -command \"& { Add-Type -A 'System.IO.Compression.FileSystem'; [IO.Compression.ZipFile]::ExtractToDirectory('configs.zip', 'algo-configs'); }\""
	echo "..."
	echo "lol j/k use unzip with explorer"
}

source env/bin/activate
ansible-playbook deploy.yml -t digitalocean,vpn,cloud -e "do_access_token=${DO_ACCESS_TOKEN} do_server_name=${DO_SERVER_NAME} do_region=${DO_REGION}"
retVal=$?
if [ ! $? -eq 0 ]; then
    echo "Sorry, there was a problem running algo. Check for an incorrect API token."
    exit $retVal
fi
compress_and_display
echo ""
echo ""
echo "--------------------------------"
echo "Thank you for using algo and AlgoVPNGen"