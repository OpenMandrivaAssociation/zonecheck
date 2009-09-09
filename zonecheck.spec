Summary:	Perform consistency checks on DNS zones
Name:		zonecheck
Version:	2.0.4
Release:	%mkrel 9
License:	GPLv2+
Group:		System/Servers
URL:		http://www.zonecheck.fr/
Source0:	%{name}-%{version}.tar.bz2
Patch0:		zonecheck-2.0.3-apache2_fix.diff
BuildRequires:	ruby >= 1.8
Requires:	ruby >= 1.8
BuildRoot:	%{_tmppath}/root-%{name}-%{version}

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
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

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

case `uname` in
	OSF1)
ruby -p -i \
	-e "\$_.gsub"\!"(/(<const\s+name\s*=\s*\"ping4\"\s+value\s*=\s*\")[^\"]*(\"\s*\/>)/, '\1/sbin/ping -n -q -t 5 -c 5 %s > /dev/null\2')" \
	-e "\$_.gsub"\!"(/(<const\s+name\s*=\s*\"ping6\"\s+value\s*=\s*\")[^\"]*(\"\s*\/>)/, '\1/sbin/ping -n -q -t 5 -c 5 %s > /dev/null\2')" \
	%{buildroot}%{_sysconfdir}/zonecheck/zc.conf
	;;

	*)
ruby -p -i \
	-e "\$_.gsub"\!"(/(<const\s+name\s*=\s*\"ping4\"\s+value\s*=\s*\")[^\"]*(\"\s*\/>)/, '\1/bin/ping -n -q -w 5 -c 5 %s > /dev/null\2')" \
	-e "\$_.gsub"\!"(/(<const\s+name\s*=\s*\"ping6\"\s+value\s*=\s*\")[^\"]*(\"\s*\/>)/, '\1/usr/sbin/ping6 -n -q -w 5 -c 5 %s > /dev/null\2')" \
	%{buildroot}%{_sysconfdir}/zonecheck/zc.conf
	;;
esac

# "Patching HTML pages" don't work it seems...
perl -pi -e "s|HTML_PATH|/zonecheck|g" %{buildroot}%{_libdir}/zonecheck/www/html/*.html.*

# install the apache config
install -d %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d
install -m0644 www/zonecheck.conf %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d/zonecheck.conf

# cleanup
rm -f %{buildroot}%{_libdir}/zonecheck/www/zonecheck.conf.in

%post www
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun www
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root,0755)
%doc BUGS ChangeLog COPYING CREDITS GPL HISTORY README TODO doc/html
%config(noreplace) %{_sysconfdir}/zonecheck/rootservers
%config(noreplace) %{_sysconfdir}/zonecheck/*.profile
%verify(not size,not md5) %config(noreplace) %{_sysconfdir}/zonecheck/zc.conf
%{_bindir}/*
%exclude %{_libdir}/zonecheck/www
%{_libdir}/zonecheck
%{_mandir}/man1/*

%files www
%defattr(-,root,root,0755)
%config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/zonecheck.conf
%{_libdir}/zonecheck/www
