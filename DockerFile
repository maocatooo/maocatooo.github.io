FROM fellah/gitbook
CMD "/bin/sh -c /usr/local/bin/gitbook install; /bin/sh -c /usr/local/bin/gitbook serve"