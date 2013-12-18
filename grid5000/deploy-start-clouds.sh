#!/bin/bash -x

set -e

ENABLE_SUNSTONE=false

function display_help()
{
  echo    "Grid 5000 script to deploy OpenNebula clouds with an OCCI server."
  echo    "Usage: $0 [-c][-h][-i file.img] -w walltime <list of cloud.yml>"
  echo -e "\t-c\t\tInstall ConPaaS once clouds are deployed (requires an OAR reservation)"
  echo -e "\t-h\t\tDisplay this help and exit"
  echo -e "\t-w hh:mm\tSet a walltime for all reservations (mandatory)"
  echo -e "\t-s\t\tEnable Sunstone"
  exit 0
}

INSTALL_CPS="no"
WALLTIME=""
while getopts chw:i:s option
do
  case $option in
    c) INSTALL_CPS="yes";;
    h) display_help;;
    w) WALLTIME=$OPTARG;;
    s) ENABLE_SUNSTONE=true;;
  esac
done
shift $(($OPTIND - 1))
CLOUDS_YML=$@

CLOUDS_YML_ARRAY=($CLOUDS_YML)
if [ ${#CLOUDS_YML_ARRAY[@]} -lt 1 ]
then
  echo "Error: this script requires at least one *.yml file."
  exit 1
fi

ALL_CLOUDS=""
for cloud_yml in $CLOUDS_YML
do
  cloud=$(basename $cloud_yml)
  ALL_CLOUDS="$ALL_CLOUDS ${cloud%.yml}"
done

if [ -z "$WALLTIME" ]
then
  echo "Mandatory argument -w walltime is missing."
  exit 1
fi

WALLTIME_MIN=$(echo $WALLTIME | sed 's/\(.*\):\(.*\)/\1*60+\2/' | bc)
NOW_MIN=$(date +"%H:%M"       | sed 's/\(.*\):\(.*\)/\1*60+\2/' | bc)
HOUR=$(( ($WALLTIME_MIN - $NOW_MIN) / 60 ))
MIN=$(( ($WALLTIME_MIN - $NOW_MIN) % 60 ))

if [ $HOUR -le 0 -a $MIN -le 0 ]
then 
  echo "Error: provided walltime cannot be after current time:"
  exit 1
fi

DURATION=$(printf "%02d:%02d:00" $HOUR $MIN)

for cloud_yml in $CLOUDS_YML
do
  sed -i "s/walltime:.*/walltime: $DURATION/" $cloud_yml
done

LOG_DIR=logs
mkdir -p $LOG_DIR
declare -A CLOUD_PIDS
for cloud in $ALL_CLOUDS
do
  echo "Deploying cloud $cloud..."
  $HOME/g5k-campaign/bin/g5k-campaign -C ${cloud}.yml -v --debug > ${LOG_DIR}/${cloud}.log 2>&1 &
  CLOUD_PIDS[$cloud]="$!"
done

for cloud in ${!CLOUD_PIDS[@]}
do
  pid="${CLOUD_PIDS[$cloud]}"
  wait $pid
  error_code="$?"
  if [ ${error_code} -eq 0 ]
  then
    echo "Deployment of cloud $cloud done (log in ${LOG_DIR}/${cloud}.log)."
  else
    echo "Error: deployment failed for cloud $cloud, error code ${error_code} (see ${LOG_DIR}/${cloud}.log)"
    exit 1
  fi
done

# get the list of cloud frontends
declare -A CLOUD_FRONTENDS
CLOUDS_CONFIG=""
for cloud in $ALL_CLOUDS
do
  FRONTEND="$(grep "frontend node is " logs/$cloud.log | sed 's/^.*frontend node is \(.*\).$/\1/')"
  CLOUD_FRONTENDS[$cloud]="$FRONTEND"
  CLOUDS_CONFIG="$CLOUDS_CONFIG ${cloud%.yml}=$FRONTEND"
done


### Configure the OCCI server on all OpenNebula frontends

CONFIG_SCRIPT=config-occi.sh

cat > $CONFIG_SCRIPT < /dev/null
chmod 755 $CONFIG_SCRIPT

for cloud in ${!CLOUD_FRONTENDS[@]}
do
  echo "Configuring cloud $cloud..."
  front=${CLOUD_FRONTENDS[$cloud]}
#  scp *.gem $front:
  # configure each front-end to run an OCCI server
  cat > $CONFIG_SCRIPT <<EOF
#!/bin/bash -x
# Set OpenNebula OCCI server: add Ruby dependencies, configure and start

set -e

echo "gem: --no-ri --no-rdoc --user-install --http-proxy http://proxy:3128" > \$HOME/.gemrc

echo "export PATH=\$PATH:\$HOME/.gem/ruby/1.9.1/bin
export GEM_HOME=\$HOME/.gem/ruby/1.9.1/
export http_proxy=http://proxy:3128
export OCCI_URL=http://$front:4567
" >> \$HOME/.profile

source \$HOME/.profile || true

gem install sinatra

occi-server stop || true

## Set host for OpenNebula 3.4
sed -i "s/^:server:.*/:server: $front/" /etc/one/occi-server.conf

## Set host for OpenNebula 3.6, 3.8.4
sed -i "s/^:host:.*/:host: $front/" /etc/one/occi-server.conf

sed -i "/:small:/ i  \ \ :custom:\n    :template: custom.erb" /etc/one/occi-server.conf



cat >> /etc/one/occi_templates/common.erb <<EOF2


# default architecture
OS = [ arch = "x86_64" ]

# override with requested architecture if any
<% @vm_info.each('OS') do |os| %>
     <% if os.attr('TYPE', 'arch') %>
       OS = [ arch = "<%= os.attr('TYPE', 'arch').split('/').last %>" ]
     <% end %>
<% end %>

# support for vnc interface (useful for debugging)
GRAPHICS = [type="vnc",listen="127.0.0.1"]
EOF2


## Fix missing version when installed from source code
if grep -q OpenNebula::VERSION /usr/lib/one/ruby/cli/one_helper.rb
then
  version=\$(grep 'VERSION = ' /usr/lib/one/ruby/cloud/CloudClient.rb | sed "s/.*VERSION = '\(.*\)'/\1/")
  sed -i "s/#{OpenNebula::VERSION}/\$version/" /usr/lib/one/ruby/cli/one_helper.rb
fi

## Print the name of the cloud in top right corner
if [ -r /usr/share/opennebula/occi/ui/public/js/locale.js ]
then
  locale_file=/usr/share/opennebula/occi/ui/public/js/locale.js
elif [ -r /usr/lib/one/ruby/cloud/occi/ui/public/js/locale.js ]
then
  locale_file=/usr/lib/one/ruby/cloud/occi/ui/public/js/locale.js
else
  echo "Error: cannot find occi/ui/public/js/locale.js neither in /usr/share/opennebula/ nor in /usr/lib/one/ruby/cloud/"
  locale_file=""
fi

if [ -n "\$locale_file" ]
then
  sed -i "
s/welcome').text(tr(\".*\"));/welcome').text(tr(\"Cloud $cloud - Welcome\"));/
" \$locale_file
fi

occi-server start

mkdir -p \$HOME/.one
echo "oneadmin:password" > \$HOME/.one/one_auth


## Set the Sunstone server if required
if $ENABLE_SUNSTONE
then
  # quiet non interactive deb commands
  export DEBIAN_FRONTEND=noninteractive
#  apt-get -q -y install opennebula-sunstone
  sunstone-server stop || true
  sed -i 's/:host:.*/:host: $front/' /etc/one/sunstone-server.conf

  ## disable the marketplace
  sed -i 's/^:marketplace_url:/#:marketplace_url:/' /etc/one/sunstone-server.conf
  # OpenNebula 3.8
  if [ -e /etc/one/sunstone-plugins.yaml ]
  then
    sed -i '/marketplace/ {N; s/:ALL:.*/:ALL: false/}' /etc/one/sunstone-plugins.yaml
  fi
  # OpenNebula 4.2
  for config_file in /etc/one/sunstone-views/user.yaml /etc/one/sunstone-views/admin.yaml /etc/one/sunstone-views/vdcadmin.yaml
  do
    if [ -e \$config_file ]
    then
      sed -i 's/marketplace-tab: true\$/marketplace-tab: false/' \$config_file
    fi
  done

  if [ -r /usr/share/opennebula/sunstone/public/js/locale.js ]
  then
    locale_file=/usr/share/opennebula/sunstone/public/js/locale.js
  elif [ -r /usr/lib/one/sunstone/public/js/locale.js ]
  then
    locale_file=/usr/lib/one/sunstone/public/js/locale.js
  else
    echo "Error: cannot find sunstone/public/js/locale.js neither in /usr/share/opennebula/ nor in /usr/lib/one/sunstone/"
    locale_file=""
  fi

  if [ -n "$locale_file" ]
  then
  sed -i "
s/welcome').text(tr(\".*\"));/welcome').text(tr(\"Cloud $cloud - Welcome\"));/
" $locale_file
  fi
  sunstone-server start
fi

EOF
  scp $CONFIG_SCRIPT root@$front:
  ssh root@$front "./$CONFIG_SCRIPT > ${CONFIG_SCRIPT%.sh}.log 2>&1"
done


if [ $INSTALL_CPS = "yes" ]
then
  ./deploy-start-conpaas.sh $CLOUDS_CONFIG
else
 echo "If you have made an OAR reservation of a single node,"
 echo "you may now deploy ConPaaS  with the following command:"
 echo "./deploy-start-conpaas.sh $CLOUDS_CONFIG"
fi
