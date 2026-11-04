; Inno Setup Script for DTU Typewriter
; Build: iscc installers\dtu_typewriter.iss

[Setup]
AppId={{B3F8A1D2-4C5E-4A7B-9D6F-1E2C3A4B5D6E}
AppName=DTU Typewriter
AppVersion=1.0
AppPublisher=DTU Computer Centre
AppPublisherURL=https://dtu.ac.in
DefaultDirName={autopf}\DTUTypewriter
DefaultGroupName=DTU Typewriter
OutputDir=..\dist
OutputBaseFilename=DTUTypewriterSetup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
WizardStyle=modern
; UninstallDisplayIcon={app}\DTUTypewriter.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\DTUTypewriter\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\DTU Typewriter"; Filename: "{app}\DTUTypewriter.exe"
Name: "{group}\{cm:UninstallProgram,DTU Typewriter}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\DTU Typewriter"; Filename: "{app}\DTUTypewriter.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\DTUTypewriter.exe"; Description: "{cm:LaunchProgram,DTU Typewriter}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Do NOT delete user data in %LOCALAPPDATA%\DTUTypewriter
Type: filesandordirs; Name: "{app}"
