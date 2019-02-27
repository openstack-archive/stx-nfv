Summary: Guest-Client
Name: guest-client
Version: 3.0.1
Release: %{tis_patch_ver}%{?_tis_dist}
License: Apache-2.0
Group: base
Packager: Wind River <info@windriver.com>
URL: unknown

Source0: %{name}-%{version}.tar.gz

%define cgcs_sdk_deploy_dir /opt/deploy/cgcs_sdk

%bcond_without systemd

%if %{with systemd}
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
BuildRequires: systemd
%endif

%package -n %{name}-devel
Summary: Guest-Client - Development files
Group: devel
Provides: guest-client-dev(x86_64) = 3.0.1-r1.0

%package -n %{name}-cgts-sdk
Summary: Guest-Client - SDK files
Group: devel
BuildRequires: json-c-devel

%description
Guest-Client with heartbeat functionality.

%description -n %{name}-devel
Guest-Client with heartbeat functionality. This package contains symbolic
links, header files, and related items necessary for software development.

%description -n %{name}-cgts-sdk
Guest-Client SDK files

%prep
%setup
# Build for guest-client package
make build sysconfdir=%{_sysconfdir}
make sample
make tar ARCHIVE_NAME=wrs-guest-heartbeat-%{version}

# Install for guest-client package
%install
make install \
     prefix=%{buildroot}/usr \
     includedir=%{buildroot}%{_includedir} \
     SDK_DEPLOY_DIR=%{buildroot}%{cgcs_sdk_deploy_dir} \
     unitdir=%{buildroot}%{_unitdir} \
     sysconfdir=%{buildroot}%{_sysconfdir}

%files
%defattr(755,root,root,-)
%{_sysconfdir}/guest-client/heartbeat/guest_heartbeat.conf
%{_sysconfdir}/guest-client/heartbeat/sample_event_handling_script
%{_sysconfdir}/guest-client/heartbeat/sample_health_check_script
%defattr(644,root,root,-)
/usr/local/lib/libguest_common_api.so.%{version}
/usr/local/lib/libguest_heartbeat_api.so.%{version}
%attr(744,-,-) /usr/local/bin/guest-client
%if %{with systemd}
%{_unitdir}/guest-client.service
%attr(744,-,-) %{_sysconfdir}/guest-client/guest-client.systemd
%endif

%preun
%if %{with systemd}
/usr/bin/systemctl stop guest-client >/dev/null 2>&1
%systemd_preun guest-client.service
systemctl reload
%endif

%post
%if %{with systemd}
%systemd_post guest-client.service
systemctl reload
/usr/bin/systemctl enable guest-client >/dev/null 2>&1
%endif

%files -n guest-client-devel
%defattr(644,root,root,-)
/usr/include/guest-client/guest_heartbeat_msg_defs.h

%files -n %{name}-cgts-sdk
%{cgcs_sdk_deploy_dir}/wrs-guest-heartbeat-%{version}.tgz
