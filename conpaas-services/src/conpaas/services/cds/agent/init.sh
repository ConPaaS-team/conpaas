#!/bin/bash

cat > /etc/init.d/edge.sh <<EOF
#!/bin/bash

/usr/local/cds/edge/edge.sh ec2-23-22-211-90.compute-1.amazonaws.com 5555 5 &
EOF

chmod +x /etc/init.d/edge.sh

cat > /etc/rc.local <<EOF
/etc/init.d/edge.sh
exit 0
EOF
