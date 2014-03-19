#!/bin/bash

# TODO	use command line arguments and/or config file to create a new service
# TODO	security: check existence of filenames we want to create

#########################################################
#                                                       #
#       Before running this script, make sure that      #
#       all previous changes are commited to SVN        #  
#                                                       #
#########################################################

# ====== replace the next 6 lines with the particulars of your new service
BP_lc_name=foobar                                   # lowercase service name in the tree
BP_mc_name=FooBar                                   # mixedcase service name in the tree
BP_uc_name=FOOBAR                                   # uppercase service name in the tree
BP_bp_name='Foo Bar'                                # selection name as shown on the frontend  create.php  page
BP_bp_desc='My brandnew FooBar Service'             # description as shown on the frontend  create.php  page
BP_bp_num=511                                       # service sequence number for conpaas-services/scripts/create_vm/create-img-script.cfg
                                                    # first look in conpaas-services/scripts/create_vm/scripts for the first free number


FILES=" conpaas-services/scripts/create_vm/create-img-script.cfg \
conpaas-services/src/conpaas/core/services.py \
conpaas-frontend/www/create.php \
conpaas-frontend/www/lib/ui/page/PageFactory.php \
conpaas-frontend/www/lib/service/factory/__init__.php \
"

#set -xv
if true
then
echo ===== adjusting =====
for i in $FILES
do
echo == $i
svn revert $i
B=`basename $i`
case $B in
        create-img-script.cfg)
                sed -i '
/BLUE_PRINT_INSERT_ON_OFF/i\
#'"$BP_lc_name"'-service = false\
'"$BP_lc_name"'-service = true
 
/BLUE_PRINT_INSERT_SECTION/i\
'"$BP_lc_name"'-service-script = '"$BP_bp_num"'-'"$BP_lc_name"'
 
                ' $i
        ;;
	select-services.sh)
		sed -i '
			/services=/s/"$/ '$BP_lc_name'&/;
			/php.* eval/s/)/|'$BP_lc_name'&/;
		' $i
	;;
	create.php)
		sed -i '
/BLUE_PRINT_INSERT/i\
			<tr class="service">\
	   			<td class="description"> <img src="images/'"$BP_lc_name"'.png" height="32" /></td>\
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
			case '"'$BP_lc_name'"':\
				require_module('"'service/$BP_lc_name'"');\
				return new '"$BP_mc_name"'Service($service_data, $manager);
		' $i
	;;
	*)
		echo "Unkown file $i" 1>&2;
		exit 100
	;;
esac
echo $i
done

echo "
You need to make your own adjustments to:
	conpaas-services/scripts/create_vm/scripts/$BP_bp_num-$BP_lc_name
"
echo =====================
fi

echo == Creating file tree from ...
find conpaas-blueprints -type f | grep -v '\.svn' | xargs file

for SOURCE_FILE in `find conpaas-blueprints -type f | grep -v '\.svn'`
do
	SF=`echo $SOURCE_FILE | sed 's,[^/]*/,,'`
	TARGET_FILE=`basename $SF | sed 's/blueprint/'"$BP_lc_name"'/ ; s/5xx-/'"$BP_bp_num"'-/'`
	TARGET_DIR=`dirname $SF | sed 's,blueprint,'"$BP_lc_name"',g'`
	[ -d $TARGET_DIR ] || mkdir -p $TARGET_DIR
	sed '
                s/Section: 5xx-/Section: '"$BP_bp_num"'-/
		s/blueprint/'"$BP_lc_name"'/g
		s/BluePrint/'"$BP_mc_name"'/g
	' $SOURCE_FILE > $TARGET_DIR/$TARGET_FILE
done


echo '
You may want to replace this file with your own version:
	conpaas-frontend/www/images/'$BP_lc_name'.png
'
svn status
