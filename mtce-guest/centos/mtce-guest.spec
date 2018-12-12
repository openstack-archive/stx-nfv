Summary: Maintenance Guest Server/Agent Package
Name: mtce-guest
Version: 1.0
%define patchlevel %{tis_patch_ver}
Release: %{tis_patch_ver}%{?_tis_dist}

License: Apache-2.0
Group: base
Packager: Wind River <info@windriver.com>
URL: unknown

Source0: %{name}-%{version}.tar.gz

BuildRequires: openssl
BuildRequires: openssl-devel
BuildRequires: json-c
BuildRequires: json-c-devel
BuildRequires: libevent
BuildRequires: libevent-devel
BuildRequires: libuuid
BuildRequires: libuuid-devel
BuildRequires: fm-common
BuildRequires: fm-common-dev
BuildRequires: guest-client-devel
BuildRequires: mtce-common-dev >= 1.0
BuildRequires: systemd-devel
BuildRequires: cppcheck

%description
Maintenance Guest Agent Service and Server assists in VM guest
heartbeat control and failure reporting at the controller level.

%package -n mtce-guestAgent
Summary: Maintenance Guest Agent Package
Group: base
Requires: dpkg
Requires: time
Requires: libjson-c.so.2()(64bit)
Requires: libstdc++.so.6(CXXABI_1.3)(64bit)
Requires: librt.so.1(GLIBC_2.2.5)(64bit)
Requires: libfmcommon.so.1()(64bit)
Requires: libstdc++.so.6(GLIBCXX_3.4.9)(64bit)
Requires: fm-common >= 1.0
Requires: libc.so.6(GLIBC_2.2.5)(64bit)
Requires: libstdc++.so.6(GLIBCXX_3.4.11)(64bit)
Requires: /bin/sh
Requires: librt.so.1()(64bit)
Requires: libc.so.6(GLIBC_2.3)(64bit)
Requires: libc.so.6(GLIBC_2.14)(64bit)
Requires: libpthread.so.0(GLIBC_2.2.5)(64bit)
Requires: librt.so.1(GLIBC_2.3.3)(64bit)
Requires: libgcc_s.so.1(GCC_3.0)(64bit)
Requires: libevent >= 2.0.21
Requires: libevent-2.0.so.5()(64bit)
Requires: libuuid.so.1()(64bit)
Requires: libm.so.6()(64bit)
Requires: rtld(GNU_HASH)
Requires: libstdc++.so.6()(64bit)
Requires: libc.so.6()(64bit)
Requires: libgcc_s.so.1()(64bit)
Requires: libstdc++.so.6(GLIBCXX_3.4)(64bit)
Requires: libstdc++.so.6(GLIBCXX_3.4.15)(64bit)
Requires: libpthread.so.0()(64bit)


%description -n mtce-guestAgent
Maintenance Guest Agent Service assists in
VM guest heartbeat control and failure reporting at the controller
level.

%package -n mtce-guestServer
Summary: Maintenance Guest Server Package
Group: base
Requires: util-linux
Requires: /bin/bash
Requires: /bin/systemctl
Requires: dpkg
Requires: libjson-c.so.2()(64bit)
Requires: libstdc++.so.6(CXXABI_1.3)(64bit)
Requires: librt.so.1(GLIBC_2.2.5)(64bit)
Requires: libfmcommon.so.1()(64bit)
Requires: libstdc++.so.6(GLIBCXX_3.4.9)(64bit)
Requires: fm-common >= 1.0
Requires: libc.so.6(GLIBC_2.2.5)(64bit)
Requires: libstdc++.so.6(GLIBCXX_3.4.11)(64bit)
Requires: /bin/sh
Requires: librt.so.1()(64bit)
Requires: libc.so.6(GLIBC_2.3)(64bit)
Requires: libc.so.6(GLIBC_2.14)(64bit)
Requires: libpthread.so.0(GLIBC_2.2.5)(64bit)
Requires: librt.so.1(GLIBC_2.3.3)(64bit)
Requires: libgcc_s.so.1(GCC_3.0)(64bit)
Requires: libevent >= 2.0.21
Requires: libevent-2.0.so.5()(64bit)
Requires: libuuid.so.1()(64bit)
Requires: libm.so.6()(64bit)
Requires: rtld(GNU_HASH)
Requires: libstdc++.so.6()(64bit)
Requires: libc.so.6(GLIBC_2.4)(64bit)
Requires: libc.so.6()(64bit)
Requires: libgcc_s.so.1()(64bit)
Requires: libstdc++.so.6(GLIBCXX_3.4)(64bit)
Requires: libstdc++.so.6(GLIBCXX_3.4.15)(64bit)
Requires: libpthread.so.0()(64bit)

%description -n mtce-guestServer
Maintenance Guest Server assists in VM guest
heartbeat control and failure reporting at the worker level.

%define local_dir /usr/local
%define local_bindir %{local_dir}/bin
%define local_sbindir %{local_dir}/sbin
%define local_etc_pmond      %{_sysconfdir}/pmon.d
%define local_etc_servicesd  %{_sysconfdir}/services.d
%define local_etc_logrotated %{_sysconfdir}/logrotate.d
%define ocf_resourced /usr/lib/ocf/resource.d

%prep
%setup

# build mtce-guestAgent and mtce-guestServer package
%build
VER=%{version}
MAJOR=$(echo $VER | awk -F . '{print $1}')
MINOR=$(echo $VER | awk -F . '{print $2}')
make MAJOR=$MAJOR MINOR=$MINOR %{?_smp_mflags} build

%global _buildsubdir %{_builddir}/%{name}-%{version}

# install mtce-guestAgent and mtce-guestServer package
%install
VER=%{version}
MAJOR=$(echo $VER | awk -F . '{print $1}')
MINOR=$(echo $VER | awk -F . '{print $2}')

install -m 755 -d %{buildroot}%{_sysconfdir}
install -m 755 -d %{buildroot}/usr
install -m 755 -d %{buildroot}/%{_bindir}
install -m 755 -d %{buildroot}/usr/local
install -m 755 -d %{buildroot}%{local_bindir}
install -m 755 -d %{buildroot}/usr/local/sbin
install -m 755 -d %{buildroot}/%{_sbindir}
install -m 755 -d %{buildroot}/lib
install -m 755 -d %{buildroot}%{_sysconfdir}/mtc
install -m 755 -d %{buildroot}%{_sysconfdir}/mtc/tmp

# resource agent stuff
install -m 755 -d %{buildroot}/usr/lib
install -m 755 -d %{buildroot}/usr/lib/ocf
install -m 755 -d %{buildroot}/usr/lib/ocf/resource.d
install -m 755 -d %{buildroot}/usr/lib/ocf/resource.d/platform
install -m 755 -p -D %{_buildsubdir}/scripts/guestAgent.ocf %{buildroot}/usr/lib/ocf/resource.d/platform/guestAgent

# config files
install -m 644 -p -D %{_buildsubdir}/scripts/guest.ini %{buildroot}%{_sysconfdir}/mtc/guestAgent.ini
install -m 644 -p -D %{_buildsubdir}/scripts/guest.ini %{buildroot}%{_sysconfdir}/mtc/guestServer.ini

# binaries
install -m 755 -p -D %{_buildsubdir}/guestServer %{buildroot}/%{local_bindir}/guestServer
install -m 755 -p -D %{_buildsubdir}/guestAgent %{buildroot}/%{local_bindir}/guestAgent

# init script files
install -m 755 -p -D %{_buildsubdir}/scripts/guestServer %{buildroot}%{_sysconfdir}/init.d/guestServer
install -m 755 -p -D %{_buildsubdir}/scripts/guestAgent %{buildroot}%{_sysconfdir}/init.d/guestAgent

# systemd service files
install -m 644 -p -D %{_buildsubdir}/scripts/guestServer.service %{buildroot}%{_unitdir}/guestServer.service
install -m 644 -p -D %{_buildsubdir}/scripts/guestAgent.service %{buildroot}%{_unitdir}/guestAgent.service

# process monitor config files
install -m 755 -d %{buildroot}%{local_etc_pmond}
install -m 644 -p -D %{_buildsubdir}/scripts/guestServer.pmon %{buildroot}%{local_etc_pmond}/guestServer.conf

# log rotation
install -m 755 -d %{buildroot}%{_sysconfdir}/logrotate.d
install -m 644 -p -D %{_buildsubdir}/scripts/guestAgent.logrotate %{buildroot}%{local_etc_logrotated}/guestAgent.logrotate
install -m 644 -p -D %{_buildsubdir}/scripts/guestServer.logrotate %{buildroot}%{local_etc_logrotated}/guestServer.logrotate

# volatile directores
install -m 755 -d %{buildroot}/var
install -m 755 -d %{buildroot}/var/run

# enable all services in systemd
%post -n mtce-guestServer
/bin/systemctl enable guestServer.service

%files -n mtce-guestAgent
%license LICENSE
%defattr(-,root,root,-)

# create mtc and its tmp dir
%dir %{_sysconfdir}/mtc
%dir %{_sysconfdir}/mtc/tmp

# config files - non-modifiable
%{_sysconfdir}/mtc/guestAgent.ini

%{_unitdir}/guestAgent.service
%{local_etc_logrotated}/guestAgent.logrotate
%{ocf_resourced}/platform/guestAgent

%{_sysconfdir}/init.d/guestAgent
%{local_bindir}/guestAgent

%files -n mtce-guestServer
%license LICENSE
%defattr(-,root,root,-)

# create mtc and its tmp dir
%dir %{_sysconfdir}/mtc
%dir %{_sysconfdir}/mtc/tmp

# config files - non-modifiable
%{_sysconfdir}/mtc/guestServer.ini

%{local_etc_pmond}/guestServer.conf
%{local_etc_logrotated}/guestServer.logrotate
%{_unitdir}/guestServer.service

%{_sysconfdir}/init.d/guestServer
%{local_bindir}/guestServer

