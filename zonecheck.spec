Summary:	Perform consistency checks on DNS zones
Name:		zonecheck
Version:	3.0.2
Release:	%mkrel 1
License:	GPLv2+
Group:		System/Servers
URL:		http://www.zonecheck.fr/
Source0:	http://www.zonecheck.fr/download/%{name}-%{version}.tgz
Patch0:		zonecheck-2.0.3-apache2_fix.diff
BuildRequires:	ruby >= 1.8
Requires:	ruby >= 1.8
BuildRoot:	%{_tmppath}/%{name}-%{version}

%description
ZoneCheck is intended to help solve DNS misconfigurations or
inconsistencies that are usually revealed by an increase in
the latency of the application. The DNS is a critical resource
for every network application, so it is quite important to
ensure that a zone or domain name is correctly configured in
the DNS.

%package	www
Summary:	Web service interface for ZoneCheck
Group:		System/Servers
Requires:	%{name} = %{version}
Requires(pre):	apache-conf >= 2.0.54
Requires(pre):	apache-mpm >= 2.0.54
Requires:	apache-mpm >= 2.0.54

%description	www
Provide a web service interface for ZoneCheck.
(ZoneCheck is intended to help solve DNS misconfigurations)

%prep

%setup -q -n %{name}
%patch0 -p0

%build

%install
rm -rf %{buildroot}

ruby ./installer.rb common cli cgi configure \
    -DRUBY=%{_bindir}/ruby \
    -DPREFIX=%{_prefix} \
    -DPROGNAME=zonecheck \
    -DHTML_PATH=/zonecheck \
    -DCHROOT=%{buildroot} \
    -DLIBEXEC=%{_libdir} \
    -DBINDIR=%{_bindir} \
    -DMANDIR=%{_mandir} \
    -DDOCDIR=%{_docdir} \
    -DETCDIR=%{_sysconfdir} \
    -DCGIDIR=%{_libdir}/zonecheck/www/cgi-bin \
    -DWWWDIR=%{_libdir}/zonecheck/www

perl -pi \
	-e 's|name="ping4" value="[^"]+"|name="ping4" value="ping -n -q -w 5 -c 5 %s > /dev/null"|;' \
	-e 's|name="ping6" value="[^"]+"|name="ping6" value="ping6 -n -q -w 5 -c 5 %s > /dev/null"|;' \
	%{buildroot}%{_sysconfdir}/zonecheck/zc.conf

# "Patching HTML pages" don't work it seems...
perl -pi -e "s|HTML_PATH|/zonecheck|g" \
    %{buildroot}%{_libdir}/zonecheck/www/html/*.html.*

# install the apache config
install -d %{buildroot}%{_webappconfdir}
install -m 644 www/zonecheck.conf %{buildroot}%{_webappconfdir}/zonecheck.conf

# cleanup
rm -f %{buildroot}%{_libdir}/zonecheck/www/zonecheck.conf.in

%post www
%if %mdkversion < 201010
%_post_webapp
%endif

%postun www
%if %mdkversion < 201010
%_postun_webapp
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc BUGS ChangeLog COPYING CREDITS GPL HISTORY README TODO doc/html
%config(noreplace) %{_sysconfdir}/zonecheck/rootservers
%config(noreplace) %{_sysconfdir}/zonecheck/*.profile
%config(noreplace) %{_sysconfdir}/zonecheck/zc.conf
%{_bindir}/*
%exclude %{_libdir}/zonecheck/www
%{_libdir}/zonecheck
%{_mandir}/man1/*

%files www
%defattr(-,root,root)
%config(noreplace) %{_webappconfdir}/zonecheck.conf
%{_libdir}/zonecheck/www
