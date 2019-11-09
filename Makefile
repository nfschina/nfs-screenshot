ARCH:=$(shell uname -m)
BIT32:=i686
BIT64:=x86_64
all:	
ifeq ($(ARCH),$(BIT64))
	tar zxvf node-webkit-v0.10.5-linux-x64.tar.gz
	cp -rf nfs node-webkit-v0.10.5-linux-x64/
	cp -rf nfs2 node-webkit-v0.10.5-linux-x64/
	cp -rf nfs-screenshot node-webkit-v0.10.5-linux-x64/
	cp -rf nfs-screenshot-autostart node-webkit-v0.10.5-linux-x64/
	cp -rf nfs-screenshot-autoclose node-webkit-v0.10.5-linux-x64/
	cp -rf cdos-start node-webkit-v0.10.5-linux-x64/
	cp -rf cdos-start-window node-webkit-v0.10.5-linux-x64/
	cp -rf cdos-start-area node-webkit-v0.10.5-linux-x64/
	cp -rf cdos-start-clipboard node-webkit-v0.10.5-linux-x64/
	cp -rf cdos-start-window-clipboard node-webkit-v0.10.5-linux-x64/
	cp -rf cdos-start-area-clipboard node-webkit-v0.10.5-linux-x64/
	cd  node-webkit-v0.10.5-linux-x64
	rm -rf libffmpegsumo.so
	rm -rf nwsnapshot
	cd ../
	chmod a+x node-webkit-v0.10.5-linux-x64/*
	#cd node-webkit-v0.10.5-linux-x64 && ./change
else
	tar zxvf node-webkit-v0.10.5-linux-ia32.tar.gz
	cp -rf nfs node-webkit-v0.10.5-linux-ia32/
	cp -rf nfs2 node-webkit-v0.10.5-linux-ia32/
	cp -rf nfs-screenshot node-webkit-v0.10.5-linux-ia32/
	cp -rf nfs-screenshot-autostart node-webkit-v0.10.5-linux-ia32/
	cp -rf nfs-screenshot-autoclose node-webkit-v0.10.5-linux-ia32/
	cp -rf cdos-start node-webkit-v0.10.5-linux-ia32/
	cp -rf cdos-start-window node-webkit-v0.10.5-linux-ia32/
	cp -rf cdos-start-area node-webkit-v0.10.5-linux-ia32/
	cp -rf cdos-start-clipboard node-webkit-v0.10.5-linux-ia32/
	cp -rf cdos-start-window-clipboard node-webkit-v0.10.5-linux-ia32/
	cp -rf cdos-start-area-clipboard node-webkit-v0.10.5-linux-ia32/
	cd  node-webkit-v0.10.5-linux-ia32
	rm -rf libffmpegsumo.so
	rm -rf nwsnapshot
	cd ../
	chmod a+x node-webkit-v0.10.5-linux-ia32/*
	#cd node-webkit-v0.10.5-linux-ia32 && ./change

endif
install:
	chmod 777 testscreenshot
	chmod 777 action
	chmod 777 nfs-screenshot.png
	chmod a+x testscreenshot
	chmod a+x action
	chmod a+x nfs-screenshot.png
	mkdir -p $(DESTDIR)/usr/bin/
	mkdir -p $(DESTDIR)/usr/lib/	
	mkdir -p $(DESTDIR)/usr/share/applications/
	mkdir -p $(DESTDIR)/usr/share/applications/nfs-screenshot
	tar zxvf libcdos-screenshot.so.tar.gz
	cp -rf libcdos-screenshot.so $(DESTDIR)/usr/lib/
	cp -rf action $(DESTDIR)/usr/bin/
	cp -rf testscreenshot $(DESTDIR)/usr/bin/
	cp -rf nfs-screenshot.desktop $(DESTDIR)/usr/share/applications/
	cp -rf nfs-screenshot-start.desktop $(DESTDIR)/usr/share/applications/nfs-screenshot
	cp -rf nfs-screenshot-close.desktop $(DESTDIR)/usr/share/applications/nfs-screenshot
	#cp -rf nw.desktop $(DESTDIR)/~/.config/autostart/
	mkdir -p $(DESTDIR)/usr/share/pixmaps/
	cp -rf nfs-screenshot.png $(DESTDIR)/usr/share/pixmaps/
ifeq ($(ARCH),$(BIT64))
	mv -f node-webkit-v0.10.5-linux-x64/* $(DESTDIR)/usr/bin
	rm -rf node-webkit-v0.10.5-linux-x64
	sed -i 's/udev\.so\.0/udev.so.1/g' $(DESTDIR)/usr/bin/nw
else
	mv -f node-webkit-v0.10.5-linux-ia32/* $(DESTDIR)/usr/bin
	rm -rf node-webkit-v0.10.5-linux-ia32
	sed -i 's/udev\.so\.0/udev.so.1/g' $(DESTDIR)/usr/bin/nw
endif


	
	

	
	
