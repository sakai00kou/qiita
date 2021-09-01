#!/bin/bash
######################################################################
# -------------------------------------------------------------------
# 【バックアップディレクトリ定義】
# ※バックアップ先、所有権、実行権変更の場合は以下を適宜変更すること
# -------------------------------------------------------------------
BACKUPDIR="/BACKUP"
BKUPDIRPERM="777"
BKUPDIROWGR="root:root"

# -------------------------------------------------------------------
# 【変数設定】
# -------------------------------------------------------------------
OPTFLG_D="0"
DATECMD=`date +%Y%m%d`
CMDNAME=${0##*/}
LOGFILE="FileBackup_`date +%Y%m%d`.csv"

# -------------------------------------------------------------------
# 【Usage関数】
# -------------------------------------------------------------------
function USAGE()
{
	echo "Usage: ${CMDNAME} [-d backupdir] backupfile"
	exit 2
}

# -------------------------------------------------------------------
# 【実行権変換関数】
# ※「rwxrwxrwx」形式の書式を「777」形式に変換する
# -------------------------------------------------------------------
function Char_to_Num()
{
	ENUM=0
	for (( i=2; i<=8; i+=3 ))
	do
		START=${i}
		END=`expr ${i} + 2`
		CHARPERM=`echo $1 | cut -c ${START}-${END}`
		case $CHARPERM in
			"rwx" | "rws" | "rwt" ) NUM=7 ;;
			"rw-" | "rwS" | "rwl" | "rwT" ) NUM=6 ;;
			"r-x" | "r-s" | "r-t" ) NUM=5 ;;
			"r--" | "r-S" | "r-l" | "r-T" ) NUM=4 ;;
			"-wx" | "-ws" | "-wt" ) NUM=3 ;;
			"-w-" | "-wS" | "-wl" | "-wT" ) NUM=2 ;;
			"--x" | "--s" | "--t" ) NUM=1 ;;
			"---" | "--S" | "--l" | "--T" ) NUM=0 ;;
		esac
		NUMPERM+=("${NUM}")

		# SUID, SGID, Sticky Bit
		if [ $(echo ${CHARPERM} | egrep "s|l|S") ]; then
			if [ ${i} == 2 ]; then
				ENUM=`expr ${ENUM} + 4`
			elif [ ${i} == 5 ]; then
				ENUM=`expr ${ENUM} + 2`
			fi
		elif [ $(echo ${CHARPERM} | egrep "t|T") ]; then
			ENUM=`expr ${ENUM} + 1` 
		fi
	done
	echo ${ENUM}${NUMPERM[0]}${NUMPERM[1]}${NUMPERM[2]}
}

# -------------------------------------------------------------------
# 【オプション処理】
# -------------------------------------------------------------------
while getopts dho: OPTION
do
	case ${OPTION} in
		# ---------------------------------------------------
		# オプション種類
		# -d : diff比較
		# -h : コマンドヘルプ
		# -o : バックアップディレクトリの変更（一時的）
		# ---------------------------------------------------
		d)	OPTFLG_D=1 ;;
		h)	USAGE ;;
		o)	BACKUPDIR=${OPTARG} ;;
		*)	break ;;
	esac
done
shift `expr ${OPTIND} - 1`

# -------------------------------------------------------------------
# コピー元ファイルパスとディレクトリパスの取得
# -------------------------------------------------------------------
if [ $# == 0 ]; then
	USAGE
elif [ $# != 1 ]; then
	echo "複数ファイルのコピーはできません"
	echo "コピー対象を１つにして下さい"
	exit 1
fi

DFULLPATH=$(cd $(dirname $1) && pwd)
FFULLPATH=$(cd $(dirname $1) && pwd)/$(basename $1)

if [ ! -e ${FFULLPATH} ]; then
	echo "$1: ファイルが存在しません"
	echo "処理を終了します"
	exit 1
fi

# -------------------------------------------------------------------
# diffコマンドによる差分比較
# -------------------------------------------------------------------
if [ ${OPTFLG_D} == 1 ]; then
	ls ${BACKUPDIR}${FFULLPATH}.* > /dev/null 2>&1
	if [ $? == 0 ]; then
		BACKUPFILE=`ls ${BACKUPDIR}${FFULLPATH}.* | tail -1`
		echo "最新のバックアップファイル ${BACKUPFILE} と比較します"
		echo "比較元：${BACKUPFILE}"
		echo "比較先：${FFULLPATH}"
		echo "------------------------------"
		diff `ls ${BACKUPDIR}${FFULLPATH}.* | tail -1` ${FFULLPATH}
		exit 0
	elif [ $? != 0 ]; then
		echo "バックアップディレクトリ ${BACKUPDIR}${DFULLPATH} にバックアップファイルが存在しません"
		exit 1
	fi
fi

# -------------------------------------------------------------------
# 【メイン処理】
# ※バックアップディレクトリ配下に階層があるかを確認し、作成、設定を
#   した上でファイルをコピーする
# -------------------------------------------------------------------
if [ -L ${FFULLPATH} ]; then
	echo "バックアップ対象はシンボリックリンクです。"
	echo "リンク先のファイルを指定して下さい。"
	exit 1
elif [ -d ${FFULLPATH} ]; then
	echo "バックアップ対象はディレクトリです。"
	echo "ファイルを指定して下さい。"
	exit 1
fi

# -------------------------------------------------------------------
# 階層構造確認と作成
# -------------------------------------------------------------------
if [ ! -e ${BACKUPDIR}${DFULLPATH} ]; then
	NF1=`echo ${BACKUPDIR} | awk -F/ '{print NF}'`
	NF2=`echo ${BACKUPDIR}${DFULLPATH} | awk -F/ '{print NF}'`

	for (( c4=${NF1}; c4<=${NF2}; c4++ ))
	do
		DIRCHECK=`echo ${BACKUPDIR}${DFULLPATH} | cut -d/ -f1-${c4}`
		if [ ! -e ${DIRCHECK} ]; then
			# -------------------------------------------
			# (${NF2}-${NF1}+1)-(${NF2}-${c4}) を式展開
			# -------------------------------------------
			ENDFIELD=`expr ${c4} - ${NF1} + 1`
			ORGDIRCHECK=`echo ${DFULLPATH} | cut -d/ -f1-${ENDFIELD}`

			if [ ${BACKUPDIR} = ${DIRCHECK} ]; then
				DPERMISSION=${BKUPDIRPERM}
				DOWNERGROUP=${BKUPDIROWGR}
			else
				DCHARPERM=`ls -l ${ORGDIRCHECK} | awk '{print $1}'`
				DPERMISSION=`Char_to_Num ${DCHARPERM}`
				DOWNERGROUP=`ls -ld ${ORGDIRCHECK} | awk '{print $3":"$4}'`
			fi

			mkdir ${DIRCHECK}
			chown ${DOWNERGROUP} ${DIRCHECK}
			chmod ${DPERMISSION} ${DIRCHECK}

			# -------------------------------------------
			# ログ書き出し
			# -------------------------------------------
			if [ ! -e ${BACKUPDIR}/${LOGFILE} ]; then
				echo "作成日,実行権,オーナ,グループ,作成ファイル・ディレクトリ" >> ${BACKUPDIR}/${LOGFILE}
			fi

			echo "`date +%Y/%m/%d`,${DPERMISSION},`echo ${DOWNERGROUP} | awk -F: '{print $1","$2}'`,${DIRCHECK}" >> ${BACKUPDIR}/${LOGFILE}
		fi
	done
else
	# -----------------------------------------------------------
	# バックアップファイル重複処理
	# -----------------------------------------------------------
	if [ -e ${BACKUPDIR}${FFULLPATH}.${DATECMD} ]; then
		c5=1
		while [ -e ${BACKUPDIR}${FFULLPATH}.${DATECMD}_${c5} ]
		do
			c5=`expr ${c5} + 1`
		done
		DATECMD=${DATECMD}_${c5}
	fi
fi

# -------------------------------------------------------------------
# ファイルコピーとパーミッション設定
# -------------------------------------------------------------------
CHARPERM=`ls -l ${FFULLPATH} | awk '{print $1}'`
FOWNERGROUP=`ls -l ${FFULLPATH} | awk '{print $3":"$4}'`
FPERMISSION=`Char_to_Num ${CHARPERM}`

cp -p ${FFULLPATH} ${BACKUPDIR}${FFULLPATH}.${DATECMD}
chown ${FOWNERGROUP} ${BACKUPDIR}${FFULLPATH}.${DATECMD}
chmod ${FPERMISSION} ${BACKUPDIR}${FFULLPATH}.${DATECMD}

# -------------------------------------------------------------------
# ログ書き出し
# -------------------------------------------------------------------
echo "`date +%Y/%m/%d`,${FPERMISSION},`echo ${FOWNERGROUP} | awk -F: '{print $1","$2}'`,${BACKUPDIR}${FFULLPATH}.${DATECMD}" >> ${BACKUPDIR}/${LOGFILE}

echo "正常終了"
echo "バックアップファイル一覧：${BACKUPDIR}/${LOGFILE}"
echo "コピー元：`ls -l ${FFULLPATH}`"
echo "コピー先：`ls -l ${BACKUPDIR}${FFULLPATH}.${DATECMD}`"

exit 0

