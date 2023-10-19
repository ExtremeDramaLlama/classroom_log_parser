# Backstory

If Classroom shows you a popup (not just a message in chat) that the student left, then you are no longer getting paid for your time, and will have to file support ticket to get your money.

I only noticed it by chance when it happened the first time last month, so I suspect it's happened before. And if it happened to me, it's probably happened to other people. 

Basically, TutorDotCom is doing wage theft. It's wage theft via incompetence , rather than malice, but it's wage theft nonetheless.

# This Script

Run it and it will look through all available log files in the `%AppDataLocal%/Tutor.com/Tutor.com Classroom/<version>/` directories.

At least for me theres a missing span of a month or two that's not anywhere to be found, not sure what's up with that. Possibly the log files are rotated, I'm not actually sure.

# The Web Version

There's a javascript version at https://extremedramallama.github.io/

For this one, since you can only upload one file at time, you might want to concatenate all the files together. You can do that using powershell:

```powershell
Get-ChildItem "$env:LOCALAPPDATA\Tutor.com\Tutor.com Classroom\*\Log.txt" | Get-Content | Out-File "$env:USERPROFILE\Desktop\FullLog.txt" -Encoding utf8
```

If you're justifiably cautious about pasting random code into your terminal, here's a breakdown of that, provided by ChatGPT: 

1. **`Get-ChildItem`** - This cmdlet retrieves items (like files and directories) from a specified location.

   - **`"$env:LOCALAPPDATA\Tutor.com\Tutor.com Classroom\*\Log.txt"`** - This specifies the path to look for the files. 
     - `$env:LOCALAPPDATA` is an environment variable that points to the local app data directory for the current user.
     - `Tutor.com\Tutor.com Classroom\*` - This navigates to the "Tutor.com Classroom" directory and uses the wildcard (`*`) to look into all directories within it.
     - `\Log.txt` - This specifies that we are only interested in files named "Log.txt".

2. **`|`** - This is the PowerShell pipeline operator. It takes the output of one command and passes it as input to the next command.

3. **`Get-Content`** - This cmdlet retrieves the content of the specified items (in this case, the "Log.txt" files).

4. **`|`** - Another pipeline operator.

5. **`Out-File`** - This cmdlet sends output to a file.

   - **`"$env:USERPROFILE\Desktop\FullLog.txt"`** - This specifies the path where the concatenated logs will be saved. 
     - `$env:USERPROFILE` is an environment variable that points to the current user's home directory.
     - `\Desktop\FullLog.txt` - This specifies that we want to save the file on the user's desktop with the name "FullLog.txt".
     
   - **`-Encoding utf8`** - This flag sets the encoding of the output file to UTF-8. By default, `Out-File` uses UTF-16LE encoding, which can cause compatibility issues with tools and languages (like Python) that expect UTF-8 encoding. By setting the encoding to UTF-8, the resulting file will be more universally compatible.

In essence, this command searches for all "Log.txt" files within the specified directory, retrieves their content, and then concatenates and writes the content to a new file on the user's desktop with UTF-8 encoding. 
