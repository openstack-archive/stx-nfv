Summary: Titanium Cloud agent and helper app to scale VMs up/down
Name: guest-scale-agent
Version: 2.0
%define patchlevel %{tis_patch_ver}
Release: %{tis_patch_ver}%{?_tis_dist}
License: Apache-2.0
Group: base
Packager: Wind River <info@windriver.com>
URL: unknown

%define cgcs_sdk_deploy_dir /opt/deploy/cgcs_sdk
Source0: %{name}-%{version}.tar.gz

BuildRequires: json-c-devel
BuildRequires: host-guest-comm-dev
BuildRequires: guest-host-comm-dev
BuildRequires: systemd-devel

Requires: bash

%description
Titanium Cloud agent and helper app to scale VMs up/down

%package -n guest-scale-agent-dbg
Summary: Titanium Cloud agent and helper app to scale VMs up/down - Debugging files
Group: devel

%description -n guest-scale-agent-dbg
Titanium Cloud agent and helper app to scale VMs up/down  This package contains ELF
symbols and related sources for debugging purposes.

%package -n guest-scale-agent-dev
Summary: Titanium Cloud agent and helper app to scale VMs up/down - Development files
Group: devel
Requires: guest-scale-agent = %{version}-%{release}

%description -n guest-scale-agent-dev
Titanium Cloud agent and helper app to scale VMs up/down  This package contains
symbolic links, header files, and related items necessary for software
development.

%package -n guest-scale-helper
Summary: Titanium Cloud agent and helper app to scale VMs up/down
Group: base
Requires: rtld(GNU_HASH)

%description -n guest-scale-helper
Titanium Cloud agent and helper app to scale VMs up/down

%package -n %{name}-cgts-sdk
Summary: SDK files for Titanium Cloud agent and helper app to scale VMs up/down
Group: devel

%description -n %{name}-cgts-sdk
SDK files for Titanium Cloud agent and helper app to scale VMs up/down
%prep
%setup


%build
VER=%{version}
MAJOR=`echo $VER | awk -F . '{print $1}'`
MINOR=`echo $VER | awk -F . '{print $2}'`
PATCH=%{patchlevel}
make all VER=${VER} MAJOR=${MAJOR} MINOR=${MINOR} PATCH=${PATCH}

%install
make install \
     DESTDIR=%{buildroot} \
     SYSCONFDIR=%{buildroot}%{_sysconfdir} \
     VERSION=%{version} PATCH=%{tis_patch_ver}\
     UNITDIR=%{buildroot}%{_unitdir} \
     SDK_DEPLOY_DIR=%{buildroot}%{cgcs_sdk_deploy_dir}

%post
%systemd_post offline-cpus.service
%systemd_post guest-scale-agent.service
/usr/bin/systemctl enable offline-cpus.service >/dev/null 2>&1
/usr/bin/systemctl enable guest-scale-agent.service >/dev/null 2>&1

%preun
%systemd_preun offline-cpus.service
%systemd_preun guest-scale-agent.service

%postun
%systemd_postun guest-scale-agent.service
%systemd_postun offline-cpus.service

%files
%defattr(-,root,root,-)

/usr/sbin/guest_scale_agent
/usr/sbin/offline_cpus
/usr/sbin/app_scale_helper
/etc/init.d/offline_cpus
%{_unitdir}/offline-cpus.service
%{_unitdir}/guest-scale-agent.service

%files -n guest-scale-agent-dbg
%defattr(-,root,root,-)

/usr/src/debug/*
/usr/sbin/.debug/guest_scale_agent

%files -n guest-scale-agent-dev
%defattr(-,root,root,-)

/usr/sbin/.debug/guest_scale_agent

%files -n guest-scale-helper
%defattr(-,root,root,-)

/usr/sbin/guest_scale_helper

%files -n %{name}-cgts-sdk
%{cgcs_sdk_deploy_dir}/wrs-guest-scale-%{version}.%{patchlevel}.tgz

