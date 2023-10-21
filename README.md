# Backstory

This is a tool intended for tutors contracted with Tutor.com. 

The software we use, Classroom, has some flaws. One of these flaws is that it will, sometimes, falsely detect that the student has left the session. The only visible symptom of this appears to be that you receive a popup (not just a message in chat) saying that the student left, even though the student is still there and the session is proceeding normally otherwise. 

At this point, you are no longer being paid for your time, and you will have to submit a support ticket, along with the log file, to get paid for that missing time. It's very easy to miss these incidents, which is why I created this tool that analyzes the log file and tries to detect them.

# Finding the Log File

The log files (plural, because Classroom keeps a separate one for each version of the software) are stored in the `%AppDataLocal%/Tutor.com/Tutor.com Classroom/<version>/` directories.

For non-nerds, you can find the log file for the current version by right clicking on the tray icon, clicking "about", and then clicking the link to the log file. This will open the file in your default text editor. You can "save as" to save a copy to your desktop so it's easy to find and upload.

If you want to scan all the previous log files, you can use this powershell one-liner to combine all the logs and output the combined log to your desktop:

```powershell
Get-ChildItem "$env:LOCALAPPDATA\Tutor.com\Tutor.com Classroom\*\Log.txt" | Get-Content | Out-File "$env:USERPROFILE\Desktop\FullLog.txt" -Encoding utf8
```

# Import Notes

This tool is not guaranteed to be perfect. Double check all results against what's shown in your [billing info](https://prv.tutor.com/nGEN/Apps/SocWinSupportingPages/Provider/BillingInfo.aspx). On that linked page, if you click on your earnings, it will show the date and times and how much you earned for every session that month. 

Note that the times shown on that billing info page are in Eastern Time, while your log file uses your local time.

This tool uses a five minute threshold to detect events, in order to prevent false positives.

# Python Version

There's also a python version if you're a nerd and want something you can script to run automatically. Which is what I plan on setting up at some point; I'll update this with instructions when I do.

The python version automatically looks through all available log files in the `%AppDataLocal%/Tutor.com/Tutor.com Classroom/<version>/` directories.

At least for me theres a missing span of a month or two that's not anywhere to be found, not sure what's up with that. Possibly the log files are rotated, I'm not actually sure.

# Concatenating the Log Files

I provided a powershell snippet earlier that combines all the log directories. Since you really shouldn't paste random code into your terminal without knowing what it does, here's a ChatGPT-provided breakdown:

```powershell
Get-ChildItem "$env:LOCALAPPDATA\Tutor.com\Tutor.com Classroom\*\Log.txt" | Get-Content | Out-File "$env:USERPROFILE\Desktop\FullLog.txt" -Encoding utf8
```

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
