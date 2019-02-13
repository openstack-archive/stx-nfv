Summary: Titanium Cloud host guest messaging agents, lib, apps
Name: host-guest-comm
Version: 2.0
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
PATCH=%{tis_patch_ver}

make all VER=${VER} MAJOR=${MAJOR} MINOR=${MINOR} PATCH=${PATCH}


%install
VER=%{version}
MAJOR=`echo $VER | awk -F . '{print $1}'`
MINOR=`echo $VER | awk -F . '{print $2}'`
PATCH=%{tis_patch_ver}
make install \
     DESTDIR=%{buildroot} \
     SYSCONFDIR=%{buildroot}%{_sysconfdir} \
     UNITDIR=%{buildroot}%{_unitdir} \
     LIBDIR=%{buildroot}%{_libdir} \
     SDK_DEPLOY_DIR=%{buildroot}%{cgcs_sdk_deploy_dir} \
     MAJOR=${MAJOR} MINOR=${MINOR} PATCH=${PATCH}


%post
/usr/bin/systemctl enable host_agent.service

%postun
/usr/bin/systemctl disable host_agent.service

%files
%defattr(-,root,root,-)

/usr/lib64/libhostguestmsg.so.2.0.%{tis_patch_ver}
/usr/lib64/libhostguestmsg.so.2.0
/usr/lib64/libhostguestmsg.so.2
/usr/sbin/host_agent
/etc/pmon.d/host_agent.conf
/etc/init.d/host_agent
%{_unitdir}/host_agent.service

%files -n guest-host-comm
%defattr(-,root,root,-)

/usr/lib64/libguesthostmsg.so.2.0.%{tis_patch_ver}
/usr/lib64/libguesthostmsg.so.2.0
/usr/lib64/libguesthostmsg.so.2
/usr/lib64/libservergroup.so.2.0.%{tis_patch_ver}
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
/usr/lib64/libguesthostmsg.so.2.0.%{tis_patch_ver}
/usr/lib64/libguesthostmsg.so.2.0
/usr/lib64/libguesthostmsg.so.2
/usr/lib64/libguesthostmsg.so
/usr/lib64/libservergroup.so.2.0.%{tis_patch_ver}
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
/usr/lib64/libhostguestmsg.so.2.0.%{tis_patch_ver}
/usr/lib64/libhostguestmsg.so.2.0
/usr/lib64/libhostguestmsg.so.2
/usr/lib64/libhostguestmsg.so

%files -n %{name}-cgts-sdk
%{cgcs_sdk_deploy_dir}/wrs-server-group-%{version}.%{tis_patch_ver}.tgz
