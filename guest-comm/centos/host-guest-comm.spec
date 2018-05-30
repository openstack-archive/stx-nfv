Summary: Titanium Cloud host guest messaging agents, lib, apps
Name: host-guest-comm
Version: 2.0
%define patchlevel %{tis_patch_ver}
Release: %{tis_patch_ver}%{?_tis_dist}

License: Apache-2.0
Group: base
Packager: Wind River <info@windriver.com>
URL: unknown

Source0: %{name}-%{version}.tar.gz

%define cgcs_sdk_deploy_dir /opt/deploy/cgcs_sdk

BuildRequires: json-c
BuildRequires: json-c-devel
BuildRequires: systemd-devel

Requires: rtld(GNU_HASH)
Requires: /bin/sh
Requires: /usr/bin/systemctl

%description
Titanium Cloud host/guest messaging agents, guest app library, guest app

%package -n guest-host-comm
Summary: Titanium Cloud host guest messaging agents, lib, apps
Group: base
Requires: rtld(GNU_HASH)
Requires(post): rtld(GNU_HASH)
Requires: systemd
Requires(post): systemd
Requires(preun): systemd

%description -n guest-host-comm
Titanium Cloud host/guest messaging agents, guest app library, guest app

%package -n guest-host-comm-dev
Summary: Titanium Cloud host guest messaging agents, lib, apps
Group: base
Requires: guest-host-comm

%description -n guest-host-comm-dev
Titanium Cloud host/guest messaging agents, guest app library, guest app

%package -n %{name}-cgts-sdk
Summary: Titanium Cloud host guest messaging SDK files
Group: devel

%description -n %{name}-cgts-sdk
Titanium Cloud host guest messaging SDK files

%package -n host-guest-comm-dbg
Summary: Titanium Cloud host guest messaging agents, lib, apps - Debugging files
Group: devel

%description -n host-guest-comm-dbg
Titanium Cloud host/guest messaging agents, guest app library, guest app. This
package contains ELF symbols and related sources for debugging purposes.

%package -n host-guest-comm-dev
Summary: Titanium Cloud host guest messaging agents, lib, apps - Development files
Group: devel
Requires: host-guest-comm = %{version}-%{release}

%description -n host-guest-comm-dev
Titanium Cloud host/guest messaging agents, guest app library, guest app  This
package contains symbolic links, header files, and related items necessary
for software development.

%prep
%setup

%build
VER=%{version}
MAJOR=`echo $VER | awk -F . '{print $1}'`
MINOR=`echo $VER | awk -F . '{print $2}'`
PATCH=%{patchlevel}

make all VER=${VER} MAJOR=${MAJOR} MINOR=${MINOR} PATCH=${PATCH}
find .
find . -name "*.tgz"

%global _buildsubdir %{_builddir}/%{name}-%{version}

%install
VER=%{version}
MAJOR=`echo $VER | awk -F . '{print $1}'`
MINOR=`echo $VER | awk -F . '{print $2}'`
PATCH=%{patchlevel}

install -m 750 -d %{buildroot}/usr/sbin
install -m 755 -d %{buildroot}/usr/lib64
install -m 755 -d %{buildroot}/usr/include
install -m 755 -d %{buildroot}/usr/include/cgcs
install -m 750 -d %{buildroot}%{_sysconfdir}/init.d
install -m 750 -d %{buildroot}%{_sysconfdir}/pmon.d
install -m 750 -d %{buildroot}%{_unitdir}

install -m 750 -d %{buildroot}/usr
install -m 750 -d %{buildroot}/usr/src
install -m 750 -d %{buildroot}/usr/src/debug
install -m 750 -d %{buildroot}/usr/src/debug/host-guest-comm-%{version}


install -m 644 %{_buildsubdir}/host_guest_msg_type.h	    %{buildroot}/usr/src/debug/host-guest-comm-%{version}/host_guest_msg_type.h
install -m 644 %{_buildsubdir}/server_group_app.c	        %{buildroot}/usr/src/debug/host-guest-comm-%{version}/server_group_app.c
install -m 644 %{_buildsubdir}/server_group.c               %{buildroot}/usr/src/debug/host-guest-comm-%{version}/server_group.c
install -m 644 %{_buildsubdir}/guest_agent.c                %{buildroot}/usr/src/debug/host-guest-comm-%{version}/guest_agent.c
install -m 644 %{_buildsubdir}/lib_host_guest_msg.c         %{buildroot}/usr/src/debug/host-guest-comm-%{version}/lib_host_guest_msg.c
install -m 644 %{_buildsubdir}/host_guest_msg.c             %{buildroot}/usr/src/debug/host-guest-comm-%{version}/host_guest_msg.c
install -m 644 %{_buildsubdir}/lib_guest_host_msg.c	        %{buildroot}/usr/src/debug/host-guest-comm-%{version}/lib_guest_host_msg.c
install -m 644 %{_buildsubdir}/host_instance_mgmt.h	        %{buildroot}/usr/src/debug/host-guest-comm-%{version}/host_instance_mgmt.h
install -m 644 %{_buildsubdir}/host_instance_mgmt.c	        %{buildroot}/usr/src/debug/host-guest-comm-%{version}/host_instance_mgmt.c
install -m 644 %{_buildsubdir}/guest_host_msg.h	            %{buildroot}/usr/src/debug/host-guest-comm-%{version}/guest_host_msg.h
install -m 644 %{_buildsubdir}/host_guest_msg.h	            %{buildroot}/usr/src/debug/host-guest-comm-%{version}/host_guest_msg.h
install -m 644 %{_buildsubdir}/host_agent.c                 %{buildroot}/usr/src/debug/host-guest-comm-%{version}/host_agent.c
install -m 644 %{_buildsubdir}/server_group.h               %{buildroot}/usr/src/debug/host-guest-comm-%{version}/server_group.h

install -m 750 %{_buildsubdir}/scripts/host_agent           %{buildroot}%{_sysconfdir}/init.d/host_agent
install -m 640 %{_buildsubdir}/scripts/host_agent.service   %{buildroot}%{_unitdir}/host_agent.service
install -m 644 %{_buildsubdir}/scripts/guest-agent.service  %{buildroot}%{_unitdir}/guest-agent.service
install -m 640 %{_buildsubdir}/scripts/host_agent.conf      %{buildroot}%{_sysconfdir}/pmon.d/host_agent.conf
install -m 750 %{_buildsubdir}/bin/host_agent               %{buildroot}/usr/sbin/host_agent
install -m 750 %{_buildsubdir}/bin/guest_agent              %{buildroot}/usr/sbin/guest_agent
install -m 750 %{_buildsubdir}/bin/server_group_app         %{buildroot}/usr/sbin/server_group_app
install -m 644 %{_buildsubdir}/guest_host_msg.h	            %{buildroot}/usr/include/cgcs/guest_host_msg.h
install -m 644 %{_buildsubdir}/host_guest_msg.h	            %{buildroot}/usr/include/cgcs/host_guest_msg.h

# Deploy to the SDK deployment directory

find .
install -d %{buildroot}%{cgcs_sdk_deploy_dir}
install -m 644 sdk/wrs-server-group-%{version}.%{patchlevel}.tgz  %{buildroot}%{cgcs_sdk_deploy_dir}/wrs-server-group-%{version}.%{patchlevel}.tgz


install -m 755 -p -D %{_buildsubdir}/lib/libguesthostmsg.so.${MAJOR}.${MINOR}.${PATCH} %{buildroot}%{_libdir}/libguesthostmsg.so.${MAJOR}.${MINOR}.${PATCH}
cd %{buildroot}%{_libdir} ; ln -s libguesthostmsg.so.$MAJOR.$MINOR.${PATCH} libguesthostmsg.so.$MAJOR.${MINOR}
cd %{buildroot}%{_libdir} ; ln -s libguesthostmsg.so.$MAJOR.$MINOR.${PATCH} libguesthostmsg.so.$MAJOR
cd %{buildroot}%{_libdir} ; ln -s libguesthostmsg.so.$MAJOR.$MINOR.${PATCH} libguesthostmsg.so

install -m 755 -p -D %{_buildsubdir}/lib/libhostguestmsg.so.${MAJOR}.${MINOR}.${PATCH} %{buildroot}%{_libdir}/libhostguestmsg.so.${MAJOR}.${MINOR}.${PATCH}
cd %{buildroot}%{_libdir} ; ln -s libhostguestmsg.so.$MAJOR.$MINOR.${PATCH} libhostguestmsg.so.$MAJOR.${MINOR}
cd %{buildroot}%{_libdir} ; ln -s libhostguestmsg.so.$MAJOR.$MINOR.${PATCH} libhostguestmsg.so.$MAJOR
cd %{buildroot}%{_libdir} ; ln -s libhostguestmsg.so.$MAJOR.$MINOR.${PATCH} libhostguestmsg.so

install -m 755 -p -D %{_buildsubdir}/lib/libservergroup.so.${MAJOR}.${MINOR}.${PATCH} %{buildroot}%{_libdir}/libservergroup.so.${MAJOR}.${MINOR}.${PATCH}
cd %{buildroot}%{_libdir} ; ln -s libservergroup.so.$MAJOR.$MINOR.${PATCH} libservergroup.so.$MAJOR.${MINOR}
cd %{buildroot}%{_libdir} ; ln -s libservergroup.so.$MAJOR.$MINOR.${PATCH} libservergroup.so.$MAJOR
cd %{buildroot}%{_libdir} ; ln -s libservergroup.so.$MAJOR.$MINOR.${PATCH} libservergroup.so

%post
/usr/bin/systemctl enable host_agent.service

%postun
/usr/bin/systemctl disable host_agent.service

%files
%defattr(-,root,root,-)

/usr/lib64/libhostguestmsg.so.2.0.%{patchlevel}
/usr/lib64/libhostguestmsg.so.2.0
/usr/lib64/libhostguestmsg.so.2
/usr/sbin/host_agent
/etc/pmon.d/host_agent.conf
/etc/init.d/host_agent
%{_unitdir}/host_agent.service

%files -n guest-host-comm
%defattr(-,root,root,-)

/usr/lib64/libguesthostmsg.so.2.0.%{patchlevel}
/usr/lib64/libguesthostmsg.so.2.0
/usr/lib64/libguesthostmsg.so.2
/usr/lib64/libservergroup.so.2.0.%{patchlevel}
/usr/lib64/libservergroup.so.2.0
/usr/lib64/libservergroup.so.2
/usr/sbin/server_group_app
/usr/sbin/guest_agent
%{_unitdir}/guest-agent.service

%preun -n guest-host-comm
%systemd_preun guest-agent.service

%post -n guest-host-comm
%systemd_post guest-agent.service
/usr/bin/systemctl enable guest-agent.service >/dev/null 2>&1

%files -n guest-host-comm-dev
%defattr(-,root,root,-)

/usr/include/cgcs/guest_host_msg.h
/usr/lib64/libguesthostmsg.so.2.0.%{patchlevel}
/usr/lib64/libguesthostmsg.so.2.0
/usr/lib64/libguesthostmsg.so.2
/usr/lib64/libguesthostmsg.so
/usr/lib64/libservergroup.so.2.0.%{patchlevel}
/usr/lib64/libservergroup.so.2.0
/usr/lib64/libservergroup.so.2
/usr/lib64/libservergroup.so

%files -n host-guest-comm-dbg
%defattr(-,root,root,-)

/usr/src/debug/host-guest-comm-2.0/server_group_app.c
/usr/src/debug/host-guest-comm-2.0/server_group.c
/usr/src/debug/host-guest-comm-2.0/guest_agent.c
/usr/src/debug/host-guest-comm-2.0/lib_host_guest_msg.c
/usr/src/debug/host-guest-comm-2.0/host_guest_msg.c
/usr/src/debug/host-guest-comm-2.0/lib_guest_host_msg.c
/usr/src/debug/host-guest-comm-2.0/host_guest_msg_type.h
/usr/src/debug/host-guest-comm-2.0/host_instance_mgmt.h
/usr/src/debug/host-guest-comm-2.0/host_instance_mgmt.c
/usr/src/debug/host-guest-comm-2.0/guest_host_msg.h
/usr/src/debug/host-guest-comm-2.0/host_guest_msg.h
/usr/src/debug/host-guest-comm-2.0/host_agent.c
/usr/src/debug/host-guest-comm-2.0/server_group.h

%files -n host-guest-comm-dev
%defattr(-,root,root,-)

/usr/include/cgcs/host_guest_msg.h
/usr/lib64/libhostguestmsg.so.2.0.%{patchlevel}
/usr/lib64/libhostguestmsg.so.2.0
/usr/lib64/libhostguestmsg.so.2
/usr/lib64/libhostguestmsg.so

%files -n %{name}-cgts-sdk
%{cgcs_sdk_deploy_dir}/wrs-server-group-%{version}.%{patchlevel}.tgz
