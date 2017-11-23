#!/bin/bash

function compress_and_display(){
	FILENAME=algo-configs-$(date +%Y%m%d)
	echo "--------------------------------------------"
	echo " Zipping configs"
	echo "--------------------------------------------"
	zip -r -9 $FILENAME.zip configs > /dev/null
	echo "-----ALGO CONFIG ZIP - START COPY BELOW-----"
	base64 $FILENAME.zip
	echo "-----ALGO CONFIG ZIP - END COPY ABOVE-----"
	echo ""
	echo "1. Scroll up to the section headed 'Congratulations!'  Your Algo server is running"
	echo "   and record the p12/ssh password, and the CA key password."
	echo ""
	echo "2. Copy the text from between the ALGO CONFIG ZIP sections. Save to a file named config.txt"
	echo "   This is a compressed encoded file containing the algo configuration, including scripts and authentication keys"
	echo ""
	echo "3. Decode and uncompress the configuration files"
	echo "   On linux/macos:"
	echo "   $ base64 -d configs.txt > configs.zip"
	echo "   $ unzip configs.zip"
	echo ""
	echo "   On windows:"
	echo ""
	echo "   certutil -decode configs.txt configs.zip"
	echo "   powershell.exe -nologo -noprofile -command \"& { Add-Type -A 'System.IO.Compression.FileSystem'; [IO.Compression.ZipFile]::ExtractToDirectory('configs.zip', 'algo-configs'); }\""
	echo "   ..."
	echo "   lol j/k use unzip with explorer"
}

source env/bin/activate
ansible-playbook deploy.yml -t digitalocean,vpn,cloud -e "do_access_token=${DO_ACCESS_TOKEN} do_server_name=${DO_SERVER_NAME} do_region=${DO_REGION}"
retVal=$?
if [ ! $retVal -eq 0 ]; then
    echo "Sorry, there was a problem running algo. Check for an incorrect API token."
    exit $retVal
fi

compress_and_display
echo ""
echo "Check out the algo readme on configuring the clients: https://github.com/trailofbits/algo/blob/master/README.md#configure-the-vpn-clients"
echo ""
echo "--------------------------------"
echo "Thank you for using algo and AlgoVPNGen"
