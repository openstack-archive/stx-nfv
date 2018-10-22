Summary: Network Function Virtualization
Name: nfv
Version: 1.0
Release: %{tis_patch_ver}%{?_tis_dist}
License: Apache-2.0
Group: base
Packager: Wind River <info@windriver.com>
URL: unknown
Source0: %{name}-%{version}.tar.gz

%define debug_package %{nil}

BuildRequires: python-setuptools

%description
Titanium Cloud Config Info

%define local_bindir /usr/bin/
%define pythonroot /usr/lib64/python2.7/site-packages

%define build_python() ( \
    pushd %1; \
    %{__python} setup.py build; \
    popd)

%define install_python() ( \
    pushd %1; \
    %{__python} setup.py install \\\
        --root=$RPM_BUILD_ROOT \\\
        --install-lib=%{pythonroot} \\\
        --prefix=/usr \\\
        --install-data=/usr/share \\\
        --single-version-externally-managed; \
    popd)

# TODO: nfv-docs

%package -n nfv-common
Requires: librt.so.1()(64bit)
Summary: Network Function Virtualization Common
Group: base

%description -n nfv-common
Network Function Virtualization Common

%package -n nfv-plugins
Summary: Network Function Virtualization Plugins
Group: base

%description -n nfv-plugins
Network Function Virtualization Plugins

%package -n nfv-tools
Summary: Network Function Virtualization Tools
Group: base

%description -n nfv-tools
Network Function Virtualization Tools

%package -n nfv-vim
Summary: Virtual Infrastructure Manager
Group: base

%description -n nfv-vim
Virtual Infrastructure Manager

%package -n nfv-client
Summary: Network Function Virtualization Client
Group: base

%description -n nfv-client
Network Function Virtualization Client

%prep
%setup

# use actual value of %{_sysconfdir} to repace @SYSCONFDIR@ in config files
# use actual value of %{pythonroot} to replace @PYTHONROOT@ in config.ini.
sed -i -e 's|@SYSCONFDIR@|%{_sysconfdir}|g' nfv-vim/scripts/vim
sed -i -e 's|@SYSCONFDIR@|%{_sysconfdir}|g' nfv-vim/scripts/vim-api
sed -i -e 's|@SYSCONFDIR@|%{_sysconfdir}|g' nfv-vim/scripts/vim-webserver
sed -i -e 's|@SYSCONFDIR@|%{_sysconfdir}|g' nfv-vim/nfv_vim/config.ini
sed -i -e 's|@PYTHONROOT@|%{pythonroot}|g' nfv-vim/nfv_vim/config.ini

%build
%build_python nfv-common
%build_python nfv-plugins
%build_python nfv-tools
%build_python nfv-vim
%build_python nfv-client

%install
%install_python nfv-common
%install_python nfv-plugins
%install_python nfv-tools
%install_python nfv-vim
%install_python nfv-client

# nfv-client
install -d -m 755 %{buildroot}%{_sysconfdir}/bash_completion.d
install -m 444 nfv-client/scripts/sw-manager.completion %{buildroot}%{_sysconfdir}/bash_completion.d/sw-manager

# nfv-plugins
install -d -m 755 %{buildroot}/%{_sysconfdir}/nfv/
install -d -m 755 %{buildroot}/%{_sysconfdir}/nfv/nfv_plugins/
install -d -m 755 %{buildroot}/%{_sysconfdir}/nfv/nfv_plugins/alarm_handlers/
install -p -D -m 600 nfv-plugins/nfv_plugins/alarm_handlers/config.ini %{buildroot}/%{_sysconfdir}/nfv/nfv_plugins/alarm_handlers/config.ini
install -d -m 755 %{buildroot}/%{_sysconfdir}/nfv/nfv_plugins/event_log_handlers/
install -p -D -m 600 nfv-plugins/nfv_plugins/event_log_handlers/config.ini %{buildroot}/%{_sysconfdir}/nfv/nfv_plugins/event_log_handlers/config.ini
install -d -m 755 %{buildroot}/%{_sysconfdir}/nfv/nfv_plugins/nfvi_plugins/
install -p -D -m 600 nfv-plugins/nfv_plugins/nfvi_plugins/config.ini %{buildroot}/%{_sysconfdir}/nfv/nfv_plugins/nfvi_plugins/config.ini
install -d -m 755 %{buildroot}/
install -p -D -m 644 nfv-plugins/scripts/nfvi-plugins.logrotate %{buildroot}/%{_sysconfdir}/logrotate.d/nfvi-plugins.logrotate

# nfv-vim
install -d -m 755 %{buildroot}/usr/lib/ocf/resource.d/nfv
install -p -D -m 755 nfv-vim/scripts/vim %{buildroot}/usr/lib/ocf/resource.d/nfv/vim
install -p -D -m 755 nfv-vim/scripts/vim-api %{buildroot}/usr/lib/ocf/resource.d/nfv/vim-api
install -p -D -m 755 nfv-vim/scripts/vim-webserver %{buildroot}/usr/lib/ocf/resource.d/nfv/vim-webserver
install -d -m 755 %{buildroot}/%{_sysconfdir}/nfv/
install -d -m 755 %{buildroot}/%{_sysconfdir}/nfv/vim/
install -p -D -m 600 nfv-vim/nfv_vim/config.ini %{buildroot}/%{_sysconfdir}/nfv/vim/config.ini
install -p -D -m 600 nfv-vim/nfv_vim/debug.ini %{buildroot}/%{_sysconfdir}/nfv/vim/debug.ini

%post -n nfv-common

%post -n nfv-plugins

%clean
rm -rf $RPM_BUILD_ROOT 

%files
%defattr(-,root,root,-)

%files -n nfv-common
%defattr(-,root,root,-)
%doc nfv-common/LICENSE
%dir %{pythonroot}/nfv_common/
%{pythonroot}/nfv_common/*
%dir %{pythonroot}/windriver_nfv_common_plugins-%{version}.0-py2.7.egg-info
%{pythonroot}/windriver_nfv_common_plugins-%{version}.0-py2.7.egg-info/*

%files -n nfv-plugins
%defattr(-,root,root,-)
%doc nfv-plugins/LICENSE
%dir %{_sysconfdir}/logrotate.d/
%{_sysconfdir}/logrotate.d/nfvi-plugins.logrotate
%dir %{_sysconfdir}/nfv/nfv_plugins/
%config(noreplace)/%{_sysconfdir}/nfv/nfv_plugins/alarm_handlers/config.ini
%config(noreplace)/%{_sysconfdir}/nfv/nfv_plugins/event_log_handlers/config.ini
%config(noreplace)/%{_sysconfdir}/nfv/nfv_plugins/nfvi_plugins/config.ini
%{_sysconfdir}/nfv/nfv_plugins/*
%dir %{pythonroot}/nfv_plugins/
%{pythonroot}/nfv_plugins/*
%dir %{pythonroot}/windriver_nfv_plugins-%{version}.0-py2.7.egg-info
%{pythonroot}/windriver_nfv_plugins-%{version}.0-py2.7.egg-info/*

%files -n nfv-tools
%defattr(-,root,root,-)
%doc nfv-tools/LICENSE
%{local_bindir}/nfv-forensic
%{local_bindir}/nfv-notify
%dir %{pythonroot}/nfv_tools/
%{pythonroot}/nfv_tools/*
%dir %{pythonroot}/nfv_tools-%{version}.0-py2.7.egg-info
%{pythonroot}/nfv_tools-%{version}.0-py2.7.egg-info/*

%files -n nfv-vim
%defattr(-,root,root,-)
%doc nfv-vim/LICENSE
%{local_bindir}/nfv-vim
%{local_bindir}/nfv-vim-api
%{local_bindir}/nfv-vim-manage
%{local_bindir}/nfv-vim-webserver
%dir %{_sysconfdir}/nfv/vim/
%config(noreplace)/%{_sysconfdir}/nfv/vim/config.ini
%config(noreplace)/%{_sysconfdir}/nfv/vim/debug.ini
%dir /usr/lib/ocf/resource.d/nfv/
/usr/lib/ocf/resource.d/nfv/vim
/usr/lib/ocf/resource.d/nfv/vim-api
/usr/lib/ocf/resource.d/nfv/vim-webserver
%dir %{pythonroot}/nfv_vim/
%{pythonroot}/nfv_vim/*
%dir %{pythonroot}/nfv_vim-%{version}.0-py2.7.egg-info
%{pythonroot}/nfv_vim-%{version}.0-py2.7.egg-info/*

%files -n nfv-client
%defattr(-,root,root,-)
%doc nfv-client/LICENSE
%{local_bindir}/sw-manager
%{_sysconfdir}/bash_completion.d/sw-manager
%dir %{pythonroot}/nfv_client/
%{pythonroot}/nfv_client/*
%dir %{pythonroot}/nfv_client-%{version}.0-py2.7.egg-info
%{pythonroot}/nfv_client-%{version}.0-py2.7.egg-info/*
