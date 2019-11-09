#
# Regular cron jobs for the nfs-screenshot package
#
0 4	* * *	root	[ -x /usr/bin/nfs-screenshot_maintenance ] && /usr/bin/nfs-screenshot_maintenance
