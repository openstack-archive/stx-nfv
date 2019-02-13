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

%define local_bindir /usr/local/bin

%prep
%setup

# build mtce-guestAgent and mtce-guestServer package
%build
VER=%{version}
MAJOR=$(echo $VER | awk -F . '{print $1}')
MINOR=$(echo $VER | awk -F . '{print $2}')
make MAJOR=$MAJOR MINOR=$MINOR %{?_smp_mflags} build

# install mtce-guestAgent and mtce-guestServer package
%install
make install \
     DESTDIR=%{buildroot} \
     PREFIX=%{buildroot}/usr/local \
     SYSCONFDIR=%{buildroot}%{_sysconfdir} \
     LOCALBINDIR=%{buildroot}%{local_bindir} \
     UNITDIR=%{buildroot}%{_unitdir}

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
%{_sysconfdir}/logrotate.d/guestAgent.logrotate
/usr/lib/ocf/resource.d/platform/guestAgent

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

%{_sysconfdir}/pmon.d/guestServer.conf
%{_sysconfdir}/logrotate.d/guestServer.logrotate
%{_unitdir}/guestServer.service

%{_sysconfdir}/init.d/guestServer
%{local_bindir}/guestServer
