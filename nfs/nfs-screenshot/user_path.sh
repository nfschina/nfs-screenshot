#!/bin/bash
user1=`users`
echo $user1 >/usr/bin/nfs/nfs-screenshot/row.txt
for line in `cat /usr/bin/nfs/nfs-screenshot/row.txt`
do
filename=/home/$line/.locale
if [ ! -d "$filename" ]; then
	mkdir -p $filename/zh_CN/LC_MESSAGES/
fi
done
cp /usr/bin/nfs/nfs-screenshot/nfs_dialog.mo $filename/zh_CN/LC_MESSAGES/
chown  $user1:$user1 -R $filename
