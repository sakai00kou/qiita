rem ********************************************************************
rem ����AP�D��x�ύX�c�[��
rem ********************************************************************
@echo off

rem ********************************************************************
rem �ϐ��̏�����
rem ********************************************************************
:startssidmgr
set INTERFACE_NAME="Wi-Fi"
set NUM=
set SSID=
set RSID=
set IFNAME=
set PRIORITY=
set Rtry=

rem ********************************************************************
rem �Θb�����j���[�\��
rem ********************************************************************
cls
echo ----------------���j���[----------------
echo [1] �o�^�ςݖ���AP�̗D�揇�ʂ��m�F
echo [2] ����AP�̗D�揇�ʂ̕ύX
echo [3] �o�^�ς݂̖���LAN�v���t�@�C���폜
echo [4] ���̏������I������
echo -----------------------------------------
set /p NUM="���s���鏈�����L�ڂ��ꂽ�ԍ�����͂��Ă������� >"
if "%NUM%"=="1" (
  goto showaplist
) else if "%NUM%"=="2" (
  goto apmod
) else if "%NUM%"=="3" (
  goto apDel
) else if "%NUM%"=="4" (
  goto endMsg
) else (
  goto NoNumber
)

rem ********************************************************************
rem [1] �D�揇�ʂ̊m�F
rem ********************************************************************
:showaplist
netsh wlan show profiles
pause
goto startssidmgr

rem ********************************************************************
rem [2] �D�揇�ʂ̕ύX�O�m�F
rem ********************************************************************
:apmod
cls
netsh wlan show profiles
echo;
echo ���ォ�珇��1(�D��x��)�`n(�D��x��)
echo;
set /p SSID="�D�揇�ʂ�ύX����v���t�@�C��������͂��Ă��������B >"
set /p PRIORITY="�ύX��̗D�揇�ʂ𐔎��œ��͂��Ă��������B >"

:ExecSSIDmod
echo;
echo ���̃z�X�g�i%COMPUTERNAME%�j�ŗ��p���閳��LAN�v���t�@�C��"%SSID%"��
echo �D�揇�ʂ�"%PRIORITY%"�ɕύX���܂��B
echo;
set /p Rtry="�ύX�̎��s��[Y]�A�L�����Z����[N]����͂�Enter�L�[���������Ă��������B >"
if /i %Rtry% == y (goto startSSIDmod)
if /i %Rtry% == n (goto startssidmgr)
echo;
echo [Y]es��[N]o����͂���Enter�L�[���������Ă��������B
echo;
goto ExecSSIDmod

rem ********************************************************************
rem [2] �D�揇�ʂ̕ύX����
rem ********************************************************************
:startSSIDmod
netsh wlan set profileorder name="%SSID%" interface="%INTERFACE_NAME%" priority=%PRIORITY%
echo;
echo --------------------------------------------------
echo "%SSID%"�̗D�揇�ʂ�"%PRIORITY%"�ɂȂ�܂����B
echo --------------------------------------------------
echo;
netsh wlan show profiles

rem ********************************************************************
rem �ċA�����̊m�F
rem ********************************************************************
echo --------------------------------------------------------------
set /p Rtry="�������p������ɂ�[Y]�A���̏������I������ɂ�[N]����͂�Enter�L�[���������Ă��������B >"
echo %CONTINUE%
if /i %Rtry% == y (goto apmod)
if /i %Rtry% == n (goto startssidmgr)

rem ********************************************************************
rem [3] �o�^�ςݖ���LAN�v���t�@�C���폜�O�m�F
rem ********************************************************************
:apDel
cls
netsh wlan show profile
echo;
set /p SSID="�폜����v���t�@�C��������͂��Ă��������B >"
set /p RSID="�m�F�̂��߂�����x���͂��Ă��������B >"
if %SSID%==%RSID% goto ExecDel
echo;
echo ���͂Ɍ�肪����܂��B���͂��m�F���Ă��������B
echo;
goto apDel

:ExecDel
echo;
echo ���̃z�X�g�i%COMPUTERNAME%�j���疳��LAN�v���t�@�C����"%SSID%"���폜���܂��B
echo;
set /p Rtry="�폜���s��[Y]�A�L�����Z����[N]����͂�Enter�L�[���������Ă��������B >"
if /i %Rtry% == y (goto startapDel)
if /i %Rtry% == n (goto startssidmgr)
echo;
echo [Y]es��[N]o����͂���Enter�L�[���������Ă��������B
echo;
goto ExecDel

rem ********************************************************************
rem [3] �o�^�ςݖ���LAN�v���t�@�C���폜����
rem ********************************************************************
:startapDel
netsh wlan delete profile name="%SSID%"
echo;
echo ------------------------------------
echo "%SSID%"�̃v���t�@�C���폜�������������܂����B
echo ------------------------------------
echo;
netsh wlan show profiles

rem ********************************************************************
rem �ċA�����̊m�F
rem ********************************************************************
echo --------------------------------------------------------------
set /p Rtry="�������p������ɂ�[Y]�A���̏������I������ɂ�[N]����͂�Enter�L�[���������Ă��������B >"
echo %CONTINUE%
if /i %Rtry% == y (goto apDel)
if /i %Rtry% == n (goto startssidmgr)

rem ********************************************************************
rem �Θb�����j���[�̗�O����
rem ********************************************************************
:NoNumber
echo;
echo �w�肳�ꂽ�ԍ�����͂��Ă��������B
echo;
pause
goto startssidmgr

rem ********************************************************************
rem �I������
rem ********************************************************************
:endMsg
exit 0