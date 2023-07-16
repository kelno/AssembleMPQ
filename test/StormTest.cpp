/*****************************************************************************/
/* StormTest.cpp                          Copyright (c) Ladislav Zezula 2003 */
/*---------------------------------------------------------------------------*/
/* Test module for StormLib                                                  */
/*---------------------------------------------------------------------------*/
/*   Date    Ver   Who  Comment                                              */
/* --------  ----  ---  -------                                              */
/* 25.03.03  1.00  Lad  The first version of StormTest.cpp                   */
/*****************************************************************************/
#include <filesystem>
#include <string>
#include <locale>
#include <iostream>
#include <fstream>
#include <vector>
#include <codecvt>

#define _CRT_NON_CONFORMING_SWPRINTFS
#define _CRT_SECURE_NO_DEPRECATE
#define __INCLUDE_CRYPTOGRAPHY__
#define __STORMLIB_SELF__                   // Don't use StormLib.lib
#include <stdio.h>

#ifdef _MSC_VER
#include <crtdbg.h>
#endif

#include "../src/StormLib.h"
#include "../src/StormCommon.h"

#include "TLogHelper.cpp"                   // Helper class for showing test results

#ifdef _MSC_VER
#pragma warning(disable: 4505)              // 'XXX' : unreferenced local function has been removed
#include <crtdbg.h>
#pragma comment(lib, "winmm.lib")
#endif

#ifndef STORMLIB_WINDOWS
#include <dirent.h>
#endif

std::streampos GetFileSize(std::ifstream& inputFile) 
{
    std::streampos currentPosition = inputFile.tellg();
    inputFile.seekg(0, std::ios::end);
    std::streampos fileSize = inputFile.tellg();
    inputFile.seekg(currentPosition, std::ios::beg);
    return fileSize;
}

void DeleteMPQFile(auto filePath)
{
    if (std::filesystem::exists(filePath)) {
        try {
            std::filesystem::remove(filePath);
            std::cout << "File deleted successfully." << std::endl;
        }
        catch (const std::filesystem::filesystem_error& ex) {
            std::cout << "An error occurred: " << ex.what() << std::endl;
            exit(0);
        }
    }
    else {
        //std::cout << "File does not exist." << std::endl;
    }
}

void AddFileToMPQ(auto hMpq, auto& logger, const char* filePath, const char* internalPath, bool patch = true)
{
    std::string progressString("Adding file ");
    progressString += internalPath;
    logger.PrintMessage(progressString.c_str());

    std::ifstream inputFile(filePath, std::ios::binary);

    if (!inputFile.is_open())
    {
        auto error = std::string("Failed to open file ") + filePath;
        logger.PrintError(error.c_str());
        exit(0);
    }

    auto fileSize = GetFileSize(inputFile);

    auto createFileFlags = MPQ_FILE_COMPRESS | MPQ_FILE_ENCRYPTED;
    if (patch)
        createFileFlags |= MPQ_FILE_PATCH_FILE;

    auto writeFileFlags = MPQ_COMPRESSION_ZLIB;
    HANDLE hFile = NULL;

    if (!SFileCreateFile(hMpq, internalPath, 0, fileSize, 0, createFileFlags, &hFile))
    {
        logger.PrintError("Failed to create file");
        exit(0);
    }

    std::vector<char> buffer(fileSize);
    inputFile.read(buffer.data(), fileSize);

    if (!SFileWriteFile(hFile, buffer.data(), fileSize, writeFileFlags))
    {
        logger.PrintError("Failed to write file");
        exit(0);
    }
}

auto GetMpqPath()
{
    auto mpqFileName = "test.MPQ";
    DeleteMPQFile(mpqFileName);

    std::filesystem::path currentPath = std::filesystem::current_path();
    std::string currentDirectory = currentPath.string() + '/' + mpqFileName;

    if constexpr (!std::is_same_v<TCHAR, char>) {
        std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>> converter;
        std::wstring wide = converter.from_bytes(currentDirectory);
        return wide;
    }
    else
        return currentDirectory;
}

auto GetFileList(std::string_view directoryPath)
{
    std::vector<std::pair<std::string /*realPath*/, std::string /*internalPath*/>> files;
    for (const auto& entry : std::filesystem::recursive_directory_iterator(directoryPath))  // TODO: Crashes if given wrong dir?
    {
        if (entry.is_regular_file())
        {
            auto actualPath = entry.path().string();
            auto internalPath = actualPath.substr(directoryPath.length()); // Exclude directoryPath from the file path
            if (!internalPath.empty() && (internalPath[0] == '/' || internalPath[0] == '\\'))
                internalPath.erase(0, 1); // Remove the first character

            files.emplace_back(std::make_pair(actualPath, internalPath));
        }
    };

    return files;
}

int main(int argc, char* argv[])
{
    std::string directoryPath;
    if (argc > 1)
        directoryPath = argv[1];
    else
        return 1;

    // V4 seems to be supported by wow 335. We made a fix in SFileCreateArchive to actually remove MPQ_CREATE_LISTFILE 
    auto createFlags = MPQ_CREATE_ARCHIVE_V4 /*| MPQ_CREATE_LISTFILE | MPQ_CREATE_ATTRIBUTES*/; 
    auto mpqFullPath = GetMpqPath();
    TLogHelper logger("Assemble", mpqFullPath.c_str());
    HANDLE hMpq = NULL;
    DWORD dwFileCount = 0;

    auto fileList = GetFileList(directoryPath.c_str());

    if (!SFileCreateArchive(mpqFullPath.c_str(), createFlags, fileList.size(), &hMpq))
    {
        logger.PrintError("Failed to create archive");
        exit(0);
    }

    for (auto file : fileList)
        AddFileToMPQ(hMpq, logger, file.first.c_str(), file.second.c_str());

    SFileCloseArchive(hMpq);

    return 0;
}
