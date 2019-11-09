#!/bin/bash
users=`users`
echo $users >/usr/bin/nfs/nfs-screenshot/row.txt
for line in `cat /usr/bin/nfs/nfs-screenshot/row.txt`
do
filename=/home/$line/.locale
if [ ! -d "$filename" ]; then
	mkdir -p $filename
fi
done
cp /usr/bin/nfs/nfs-screenshot/nfs_dialog.mo /home/$line/.locale/
