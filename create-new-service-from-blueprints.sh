#!/bin/bash

# TODO	use command line arguments and/or config file to create a new service
# TODO	security: check existence of filenames we want to create

if false
then
BP_lc_name=foobar
BP_mc_name=FooBar
BP_uc_name=FOOBAR
BP_bp_name='Foo Bar'
BP_bp_desc='My brandnew FooBar Service'
else
BP_lc_name=htcondor
BP_mc_name=HTCondor
BP_uc_name=HTCONDOR
BP_bp_name='HTCondor'
BP_bp_desc='High Throughput Computing: Condor Pool Service'
fi
FILES=" conpaas-services/scripts/create_vm/opennebula-create-new-vm-image.sh \
conpaas-services/src/conpaas/core/services.py \
conpaas-frontend/www/create.php \
conpaas-frontend/www/lib/ui/page/PageFactory.php \
conpaas-frontend/www/lib/service/factory/__init__.php \
conpaas-services/scripts/create_vm/select-services.sh
"

#set -xv
if true
then
echo ===== adjusting =====
for i in $FILES
do
echo == $i
# svn revert $i
B=`basename $i`
case $B in
	select-services.sh)
		sed -i '
			/services=/s/"$/ '$BP_lc_name'&/;
			/php.* eval/s/)/|'$BP_lc_name'&/;
		' $i
	;;
	create.php)
		sed -i '
/BLUE_PRINT_INSERT/i\
			<tr>\
	   			<td class="description"> <img src="images/'"$BP_lc_name"'" height="32" /></td>\
	   			<td class="radio"><input type="radio" name="type" value="'"$BP_lc_name"'" /> '"$BP_bp_name"' </td>\
	   			<td class="info"> '"$BP_bp_desc"' </td>\
			</tr> 
		' $i
	;;
# Pfff, those quotes were tricky
	services.py)
		sed -i '
/BLUE_PRINT_INSERT_MANAGER/i\
                    '"'$BP_lc_name'"' : {'"'"'class'"'"' : '"'$BP_mc_name"'Manager'"'"',\
                                  '"'"'module'"'"': '"'"'conpaas.services.'"$BP_lc_name"'.manager.manager'"'"'},
/BLUE_PRINT_INSERT_AGENT/i\
                  '"'$BP_lc_name'"' : {'"'"'class'"'"' : '"'$BP_mc_name"'Agent'"'"',\
                                '"'"'module'"'"': '"'"'conpaas.services.'"$BP_lc_name"'.agent.agent'"'"'},
		' $i
	;;
	PageFactory.php)
		sed -i '
/BLUE_PRINT_INSERT/i\
			case '"'$BP_lc_name'"':\
				require_module('"'"'ui/page/'"$BP_lc_name'"');\
				return new '"$BP_mc_name"'Page($service);
		' $i
	;;
	__init__.php)
		sed -i '
/BLUE_PRINT_INSERT/i\
			case '"'$BP_lc_name'"':
				require_module('"'service/$BP_lc_name'"');
				return new '"$BP_mc_name"'Service($service_data, $manager);
		' $i
	;;
	opennebula-create-new-vm-image.sh)
		sed -i '
/BLUE_PRINT_FOR/s/#/'$BP_uc_name' #/;
/BLUE_PRINT_INSERT_SERVICE/i\
'"$BP_uc_name"'_SERVICE=true
/BLUE_PRINT_INSERT_SOFTWARE/i\
$'"$BP_uc_name"'_SERVICE || echo '"'"'cecho "===== Skipped '"$BP_uc_name"' ====="'"'"' >> $ROOT_DIR/conpaas_install\
$'"$BP_uc_name"'_SERVICE && cat <<EOF >> $ROOT_DIR/conpaas_install\
cecho "===== install packages required by '"$BP_mc_name"' ====="\
# you may want to add the software needed for your new '"$BP_mc_name"' service here\
\
EOF\

		' $i
	;;
	*)
		echo "Unkown file $i" 1>&2;
		exit 100
	;;
esac
echo $i
done

echo '
You may want to make your own adjustments to:
	conpaas-services/scripts/create_vm/opennebula-create-new-vm-image.sh
'
echo =====================
fi

echo == Creating file tree from ...
find conpaas-blueprints -type f | grep -v '\.svn' | xargs file

for SOURCE_FILE in `find conpaas-blueprints -type f | grep -v '\.svn'`
do
	SF=`echo $SOURCE_FILE | sed 's,[^/]*/,,'`
	TARGET_FILE=`basename $SF | sed 's/blueprint/'"$BP_lc_name"'/'`
	TARGET_DIR=`dirname $SF | sed 's,blueprint,'"$BP_lc_name"',g'`
	[ -d $TARGET_DIR ] || mkdir -p $TARGET_DIR
	sed '
		s/blueprint/'"$BP_lc_name"'/g
		s/BluePrint/'"$BP_mc_name"'/g
	' $SOURCE_FILE > $TARGET_DIR/$TARGET_FILE
done


echo '
You may want to replace this file with your own version:
	conpaas-frontend/www/images/'$BP_lc_name'.png
'
svn status
