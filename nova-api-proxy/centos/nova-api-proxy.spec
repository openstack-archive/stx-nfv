Summary: Nova Computer API Proxy
Name: nova-api-proxy
Version: 1.0
Release: %{tis_patch_ver}%{?_tis_dist}
License: Apache-2.0
Group: base
Packager: Wind River <info@windriver.com>
URL: unknown
Source0: %{name}-%{version}.tar.gz

%define debug_package %{nil}

BuildRequires: python-setuptools
BuildRequires: python2-pip
BuildRequires: python2-wheel
Requires: python-eventlet
Requires: python-routes
Requires: python-webob
Requires: python-paste
#TODO: Requires: oslo-config

%description
Nova Computer API Proxy

%define local_bindir /usr/bin/
%define local_initddir /etc/rc.d/init.d
%define pythonroot /usr/lib64/python2.7/site-packages
%define local_etc_systemd /etc/systemd/system/
%define local_proxy_conf /etc/proxy/

%prep
%setup

%build
%{__python} setup.py build
%py2_build_wheel

%install
%{__python} setup.py install --root=$RPM_BUILD_ROOT \
                             --install-lib=%{pythonroot} \
                             --prefix=/usr \
                             --install-data=/usr/share \
                             --single-version-externally-managed
mkdir -p $RPM_BUILD_ROOT/wheels
install -m 644 dist/*.whl $RPM_BUILD_ROOT/wheels/

install -d -m 755 %{buildroot}%{local_etc_systemd}
install -p -D -m 644 nova_api_proxy/scripts/api-proxy.service %{buildroot}%{local_etc_systemd}/api-proxy.service
install -d -m 755 %{buildroot}%{local_initddir}
install -p -D -m 755 nova_api_proxy/scripts/api-proxy %{buildroot}%{local_initddir}/api-proxy

install -d -m 755 %{buildroot}%{local_proxy_conf}
install -p -D -m 700 nova_api_proxy/nova-api-proxy.conf %{buildroot}%{local_proxy_conf}/nova-api-proxy.conf
install -p -D -m 700 nova_api_proxy/api-proxy-paste.ini %{buildroot}%{local_proxy_conf}/api-proxy-paste.ini

%clean
rm -rf $RPM_BUILD_ROOT

# Note: Package name is nova-api-proxy but import is nova_api_proxy so can't
# use '%{name}'.
%files
%defattr(-,root,root,-)
%doc LICENSE
%{local_bindir}/*
%{local_initddir}/*
%{local_etc_systemd}/*
%config(noreplace) %{local_proxy_conf}/nova-api-proxy.conf
%{local_proxy_conf}/api-proxy-paste.ini
%dir %{pythonroot}/nova_api_proxy
%{pythonroot}/nova_api_proxy/*
%{pythonroot}/api_proxy-%{version}.0-py2.7.egg-info/*

%package wheels
Summary: %{name} wheels

%description wheels
Contains python wheels for %{name}

%files wheels
/wheels/*
