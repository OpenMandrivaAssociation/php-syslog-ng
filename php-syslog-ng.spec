%define name    php-syslog-ng
%define version 2.9.8
%define release %mkrel 4

%define _requires_exceptions pear(\\(/usr/share/php-syslog-ng.*\\|/etc/php-syslog-ng/config.php\\|includes/.*\\))

Name:       %{name}
Version:    %{version}
Release:    %{release}
Summary:    Web frontend for syslog-ng
License:    GPL
Group:      System/Servers
URL:        http://code.google.com/p/php-syslog-ng/
Source0:    http://php-syslog-ng.googlecode.com/files/%{name}-%{version}.tgz
Patch:      php-syslog-ng-2.9.8-fhs.patch
Requires:   mod_php
Requires:   php-cli
Requires:   php-gd
Requires:   php-mysql
Requires:   php-xml
BuildArch:  noarch
%if %mdkversion < 201010
Requires(post):   rpm-helper
Requires(postun):   rpm-helper
%endif
BuildRoot:  %{_tmppath}/%{name}-%{version}

%description
Php-Syslog-ng is a frontend for viewing syslog-ng messages logged to MySQL in
realtime. It features customized searches based on device, priority, date,
time, and message.

%prep
%setup -q -n %{name}
%patch -p 1

%install
rm -rf %buildroot

install -d -m 755 %{buildroot}%{_var}/www/%{name}
cp -pr html/*.php %{buildroot}%{_var}/www/%{name}
cp -pr html/robots.txt %{buildroot}%{_var}/www/%{name}
cp -pr html/favicon.ico %{buildroot}%{_var}/www/%{name}
cp -pr html/css %{buildroot}%{_var}/www/%{name}
cp -pr html/images %{buildroot}%{_var}/www/%{name}
cp -pr html/install %{buildroot}%{_var}/www/%{name}
cp -pr html/userguide.doc %{buildroot}%{_var}/www/%{name}

install -d -m 755 %{buildroot}%{_sysconfdir}/%{name}
touch %{buildroot}%{_sysconfdir}/%{name}/config.php

install -d -m 755 %{buildroot}%{_var}/lib/%{name}
(cd %buildroot%{_var}/www/%{name} && ln -s ../../lib/%{name} jpcache)

install -d -m 755 %{buildroot}%{_datadir}/%{name}/bin
install -m 755 scripts/dbgen.pl %{buildroot}%{_datadir}/%{name}/bin
install -m 755 scripts/resetusers.sh %{buildroot}%{_datadir}/%{name}/bin
install -m 644 scripts/*.php %{buildroot}%{_datadir}/%{name}/bin

# distribut include content
pushd html
find includes -type f -a -not -name '*.js' | \
    tar --create --files-from - --remove-files | \
    (cd %{buildroot}%{_datadir}/%{name} && tar --preserve --extract)
find includes -type f -a -name '*.js' | \
    tar --create --files-from - --remove-files | \
    (cd %{buildroot}%{_var}/www/%{name} && tar --preserve --extract)
popd

# apache conf
install -d -m 755 %{buildroot}%{_webappconfdir}
cat > %{buildroot}%{_webappconfdir}/php-syslog-ng.conf <<EOF
Alias /php-syslog-ng %{_var}/www/%{name}

<Directory "%{_var}/www/%{name}">
    Order allow,deny
    Allow from all
    php_value memory_limit 128M 
    php_value max_execution_time 300
</Directory>

<Directory "%{_var}/www/%{name}/install">
    Allow from localhost
</Directory>
EOF

%post
%if %mdkversion < 201010
%_post_webapp
%endif

%postun
%if %mdkversion < 201010
%_postun_webapp
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc html/CHANGELOG html/LICENSE html/README html/TROUBLESHOOTING-INSTALL
%config(noreplace) %{_webappconfdir}/php-syslog-ng.conf
%dir %{_sysconfdir}/php-syslog-ng
%config(noreplace) %attr(-,apache,apache) %{_sysconfdir}/php-syslog-ng/config.php
%{_var}/www/%{name}
%attr(-,apache,apache) %{_var}/lib/%{name}
%{_datadir}/%{name}
