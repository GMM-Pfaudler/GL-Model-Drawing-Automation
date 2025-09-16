using System.IO;
using Autodesk.Connectivity.WebServices;
using Autodesk.Connectivity.WebServicesTools;
using Autodesk.DataManagement.Client.Framework.Forms.SkinUtils;
using Autodesk.DataManagement.Client.Framework.Vault.Currency.Connections;
using Microsoft.AspNetCore.Mvc;
using ACW = Autodesk.Connectivity.WebServices;

namespace VaultWebApplication.Controllers
{

    public class VaultConn
    {
        public Connection getConnectionObject()
        {
            try
            {
                ServerIdentities mServerId = new();
                Connection? conn = null;
                mServerId.DataServer = "172.30.0.14";
                mServerId.FileServer = "172.30.0.14";
                string mVaultName = "Pfaudler_Glass_Lined_Technology";

                LicensingAgent mLicAgent = LicensingAgent.Client; //Client | Server | None
                WebServiceManager mVault = null;
                UserPasswordCredentials mCred = null;

                WinAuthCredentials winAuthCredentials = new WinAuthCredentials(mServerId, mVaultName, null, mLicAgent);
                mVault = new WebServiceManager(winAuthCredentials);

                conn = new Connection(mVault, mVaultName, mVault.SecurityService.Session.User.Id, mServerId.DataServer, AuthenticationFlags.Standard);

                return conn;
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error: Vault connection failed: ", ex.Message);
                throw new Exception("Error: Vault connection failed: " + ex.Message);
            }
        }


        public Stream getFileStream(ACW.File file)
        {
            try
            {
                string folderPath = "$/Designs/ASSEMBLY/SO NO";
                Connection conn = getConnectionObject();
                WebServiceManager serviceManager = conn.WebServiceManager;
                Folder folder = serviceManager.DocumentService.GetFolderByPath(folderPath); // "D:\Vault\Designs\ASSEMBLY\SO NO\GLE004056-GALAXY"
                ACW.File[] files = serviceManager.DocumentService.GetLatestFilesByFolderId(folder.Id, false);
                ACW.File localFile = serviceManager.DocumentService.GetFileById(file.Id);
                var FileDownloadTicket = serviceManager.DocumentService.GetDownloadTicketsByFileIds(new long[] { file.Id });
                FilestoreService fileStoreService = serviceManager.FilestoreService;
                var fileStream = fileStoreService.DownloadFilePart(FileDownloadTicket[0].Bytes, 0, localFile.FileSize, false);
                return fileStream;
            }
            catch (Exception ex)
            {
                throw new Exception(ex.Message);
            }
        }

        public void GetAssemblyAssociations(long fileId, DocumentService docService)
        {
            var fileAssocArray = docService.GetFileAssociationsByIds(
                new long[] { fileId },
                FileAssociationTypeEnum.None, // Main relationships
                false, // no parent recursion
                FileAssociationTypeEnum.All, // main children
                true, // no child recursion
                false, // do not include related documents (e.g. .dwg, .idw)
                false  // do not include hidden files
            );

            var assocs = fileAssocArray?.FirstOrDefault()?.FileAssocs;
            if (assocs == null || assocs.Length == 0)
            {
                Console.WriteLine("No child components found.");
                return;
            }

            List<FileAssoc> listOfAssocFiles = new List<FileAssoc>(); 

            foreach (var assoc in assocs)
            {
                var childFile = assoc.CldFile;

                // Filter: Only .iam and .ipt
                if (!childFile.Name.EndsWith(".iam", StringComparison.OrdinalIgnoreCase) &&
                    !childFile.Name.EndsWith(".ipt", StringComparison.OrdinalIgnoreCase))
                {
                    continue;
                }

                listOfAssocFiles.Add(assoc);
                //Console.WriteLine($"- {childFile.Name} | Qty: {assoc.Quantity} | " +
                //                  $"Version: {childFile.VerNum} | Path: {childFile.FullName}");
            }
            Console.WriteLine(listOfAssocFiles[0]);
        }

    }


    public class FileTransferItem
    {
        public string Path { get; set; }           // Full local file path
        public string Base64Content { get; set; }  // Base64 of file bytes
    }

    public class BulkUploadRequest
    {
        public List<PartModel> Parts { get; set; }
        public string FileName { get; set; }
        
    }


    public class PartModel
    {
        public string? PartNumber { get; set; } // Nullable
        public string? Keywords { get; set; }  // Nullable
        public string? REV { get; set; }       // Nullable
    }

    public class ComponentItemCode
    {
        public string Comp { get; set; }
        public string ItemCode { get; set; }
        public string PartNumber { get; set; }
        public string Member { get; set; }
        
    }

    public class ComponentItemCodes
    {
        public List<ComponentItemCode> Items { get; set; }
    }

    //public class ComponentItemCodes
    //{
    //    public List<string> ItemCodes { get; set; }
    //}

    public class SearchFilesItemCodes
    {
        public ACW.File SearchFile { get; set; }

        public string ItemCode { get; set; }
    }

    [ApiController]
    [Route("api/[controller]")]
    public class VaultController : ControllerBase
    {

        [HttpGet("connect")]
        public IActionResult ConnectToVault()
        {
            try
            {
                VaultConn vault = new();
                Connection conn = vault.getConnectionObject();
                string login_user_name = conn.WebServiceManager.AuthService.Session.User.Name;

                //WebServiceManager serviceManager = conn.WebServiceManager;
                //ACW.Folder folder = serviceManager.DocumentService.GetFolderByPath("$/Designs/ASSEMBLY/SO NO/GLE004056-GALAXY"); // "D:\Vault\Designs\ASSEMBLY\SO NO\GLE004056-GALAXY"
                //ACW.File[] files = serviceManager.DocumentService.GetLatestFilesByFolderId(folder.Id, false);
                //ACW.File file = files[0];
                //Autodesk.Connectivity.WebServices.File localFile = serviceManager.DocumentService.GetFileById(file.Id);
                //var FileDownloadTicket = serviceManager.DocumentService.GetDownloadTicketsByFileIds(new long[] { file.Id });
                //FilestoreService fileStoreService = serviceManager.FilestoreService;
                //var fileStream = fileStoreService.DownloadFilePart(FileDownloadTicket[0].Bytes, 0, localFile.FileSize, false);



                //if (files != null && files.Any())
                //{
                //    foreach (ACW.File file in files)
                //    {
                //        //Sample code to download the files
                //        string localPath = "D:\\Vault\\Designs\\ASSEMBLY\\SO NO\\GLE004056-GALAXY"; // AppDomain.CurrentDomain.BaseDirectory;
                //        Autodesk.Connectivity.WebServices.File localFile = serviceManager.DocumentService.GetFileById(file.Id);
                //        var FileDownloadTicket = serviceManager.DocumentService.GetDownloadTicketsByFileIds(new long[] { file.Id });
                //        FilestoreService fileStoreService = serviceManager.FilestoreService;
                //        var fileStream = fileStoreService.DownloadFilePart(FileDownloadTicket[0].Bytes, 0, localFile.FileSize, false);

                //        byte[] bytes;
                //        var reader = new StreamReader(fileStream);
                //        bytes = System.Text.Encoding.UTF8.GetBytes(reader.ReadToEnd());
                //        System.IO.File.WriteAllBytes(localPath, bytes);
                //    }
                //}

                //var stream = new MemoryStream(fileBytes); // Can use FileStream for large files
                //stream.Position = 0;

                //return File(fileStream, "application/octet-stream", file.Name);
                return Ok(new { success = true, message = "Connected to Vault successfully. : " + login_user_name });
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error: Vault connection failed: ", ex.Message);
                return StatusCode(500, new { success = false, message = "Vault connection failed.", error = ex.Message });
            }
        }

        [HttpGet("get/{fileName}")]
        public IActionResult getFileFromVault(string fileName)
        {
            try
            {
                VaultConn vault = new();
                Connection conn = vault.getConnectionObject();
                Console.WriteLine("File Name: " + fileName);
                WebServiceManager serviceManager = conn.WebServiceManager;
                Folder folder = serviceManager.DocumentService.GetFolderByPath("$/Designs/ASSEMBLY/SO NO");
                ACW.File[] files = serviceManager.DocumentService.GetLatestFilesByFolderId(folder.Id, false);
                ACW.File file = files[0];
                ACW.File localFile = serviceManager.DocumentService.GetFileById(file.Id);
                var FileDownloadTicket = serviceManager.DocumentService.GetDownloadTicketsByFileIds(new long[] { file.Id });
                FilestoreService fileStoreService = serviceManager.FilestoreService;
                var fileStream = fileStoreService.DownloadFilePart(FileDownloadTicket[0].Bytes, 0, localFile.FileSize, false);
                return File(fileStream, "application/octet-stream", file.Name);
            }
            catch (Exception ex) {
                return StatusCode(500, new { success = false, message = "Vault connection failed.", error = ex.Message });
            }
        }

        [HttpPost("findcomponents")]
        public IActionResult findComponents([FromBody] ComponentItemCodes request)
        {
            try
            {
                if (request == null || request.Items == null || !request.Items.Any())
                    return BadRequest("Invalid data.");

                VaultConn vault = new();
                Connection conn = vault.getConnectionObject();
                PropDef[] filePropDefs = conn.WebServiceManager.PropertyService.GetPropertyDefinitionsByEntityClassId("FILE");
                PropDef itemCodePropDef = filePropDefs.Single(n => n.DispName == "Item_Code");
                PropDef memberPropDef = filePropDefs.Single(n => n.DispName == "File Name");


                var result = new List<object>();

                foreach (var item in request.Items)
                {
                    var code = item.ItemCode;
                    var comp = item.Comp;
                    var partnumber = item.PartNumber;
                    var member = item.Member;

                    if (code != "")
                    {
                        SrchCond searchFileByItemCode = new SrchCond()
                        {
                            PropDefId = itemCodePropDef.Id,
                            PropTyp = PropertySearchType.SingleProperty,
                            SrchOper = 3,
                            SrchRule = SearchRuleType.Must,
                            SrchTxt = code
                        };

                        string bookmark = string.Empty;
                        SrchStatus status = null;
                        List<ACW.File> tempTotalResults = new List<ACW.File>();

                        while (status == null || tempTotalResults.Count < status.TotalHits)
                        {
                            var results = conn.WebServiceManager.DocumentService.FindFilesBySearchConditions(
                                new SrchCond[] { searchFileByItemCode },
                                null, null, false, true, ref bookmark, out status);

                            if (results != null)
                                tempTotalResults.AddRange(results);
                            else
                                break;
                        }

                        var latest = tempTotalResults.OrderByDescending(f => f.VerNum).FirstOrDefault();
                        if (latest != null)
                        {
                            var latestFile = conn.WebServiceManager.DocumentService.GetLatestFileByMasterId(latest.MasterId);
                            var folder = conn.WebServiceManager.DocumentService.GetFolderById(latestFile.FolderId);
                            var localFolderPath = folder.FullName.Replace("$", "D:").Replace("/", "\\");
                            string localFilePath = Path.Combine(localFolderPath, latestFile.Name);

                            var fileStream = vault.getFileStream(latestFile);
                            using var memoryStream = new MemoryStream();
                            fileStream.CopyTo(memoryStream);
                            byte[] fileBytes = memoryStream.ToArray();

                            result.Add(new
                            {
                                component = comp,
                                itemcode = code,
                                filepath = localFilePath,
                                base64 = Convert.ToBase64String(fileBytes)
                            });
                        }
                    }
                    else if(member != "")
                    {
                        SrchCond searchFileByItemCode = new SrchCond()
                        {
                            PropDefId = memberPropDef.Id,
                            PropTyp = PropertySearchType.SingleProperty,
                            SrchOper = 1,
                            SrchRule = SearchRuleType.Must,
                            SrchTxt = member
                        };

                        string bookmark = string.Empty;
                        SrchStatus status = null;
                        List<ACW.File> tempTotalResults = new List<ACW.File>();

                        while (status == null || tempTotalResults.Count < status.TotalHits)
                        {
                            var results = conn.WebServiceManager.DocumentService.FindFilesBySearchConditions(
                                new SrchCond[] { searchFileByItemCode },
                                null, null, false, true, ref bookmark, out status);

                            if (results != null)
                                tempTotalResults.AddRange(results);
                            else
                                break;
                        }

                        var latest = tempTotalResults.OrderByDescending(f => f.VerNum).FirstOrDefault();
                        if (latest != null)
                        {
                            var latestFile = conn.WebServiceManager.DocumentService.GetLatestFileByMasterId(latest.MasterId);
                            var folder = conn.WebServiceManager.DocumentService.GetFolderById(latestFile.FolderId);
                            var localFolderPath = folder.FullName.Replace("$", "D:").Replace("/", "\\");
                            string localFilePath = Path.Combine(localFolderPath, latestFile.Name);

                            var fileStream = vault.getFileStream(latestFile);
                            using var memoryStream = new MemoryStream();
                            fileStream.CopyTo(memoryStream);
                            byte[] fileBytes = memoryStream.ToArray();

                            result.Add(new
                            {
                                component = comp,
                                itemcode = code,
                                filepath = localFilePath,
                                base64 = Convert.ToBase64String(fileBytes)
                            });
                        }
                    }
                }

                return Ok(result);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { success = false, message = "Failed to checkout.", error = ex.Message });
            }
        }


        //[HttpPost("findcomponents")]
        //public IActionResult findComponents([FromBody] ComponentItemCodes request)
        //{
        //    try
        //    {
        //        VaultConn vault = new();
        //        Connection conn = vault.getConnectionObject();
        //        PropDef[] filePropDefs = conn.WebServiceManager.PropertyService.GetPropertyDefinitionsByEntityClassId("FILE");
        //        PropDef itemCodePropDef = filePropDefs.Single(n => n.DispName == "Item_Code");

        //        if (request == null || request.ItemCodes == null || !request.ItemCodes.Any())
        //            return BadRequest("Invalid data.");

        //        List<string> itemCodes = request.ItemCodes;

        //        List<ACW.File> searchedFilesList = new List<ACW.File>();

        //        List<SearchFilesItemCodes> searchFilesItemCodesList = new List<SearchFilesItemCodes>();

        //        foreach (var code in request.ItemCodes)
        //        {

        //            SrchCond searchFileByItemCode = new SrchCond()
        //            {
        //                PropDefId = itemCodePropDef.Id,
        //                PropTyp = PropertySearchType.SingleProperty,
        //                SrchOper = 3, // 1 = contains, 3 = Is exactly (or equals)
        //                SrchRule = SearchRuleType.Must,
        //                SrchTxt = code
        //            };

        //            string bookmark = string.Empty;
        //            SrchStatus status = null;
        //            List<ACW.File> tempTotalResults = new List<ACW.File>();

                    

        //            while (status == null || tempTotalResults.Count < status.TotalHits)
        //            {
        //                ACW.File[] results = conn.WebServiceManager.DocumentService.FindFilesBySearchConditions(
        //                    new SrchCond[] { searchFileByItemCode },
        //                    null, null, false, true, ref bookmark, out status);

        //                if (results != null)
        //                {
        //                    foreach(ACW.File file in results)
        //                    {
        //                        var searchedFile = new SearchFilesItemCodes
        //                        {
        //                            SearchFile = file,
        //                            ItemCode = code
        //                        };
        //                        searchFilesItemCodesList.Add(searchedFile);
        //                    };
        //                    tempTotalResults.AddRange(results);
        //                }
        //                else
        //                    break;
        //            }
        //            Console.WriteLine($"tempTotalResults search files: {tempTotalResults.Count}");
        //            // Adding all searched files.
        //            searchedFilesList.AddRange(tempTotalResults);

        //        }

        //        var result = new List<FileTransferItem>();

        //        var filteredList = searchFilesItemCodesList.GroupBy(x => x.ItemCode).Select(g => g.OrderByDescending(x => x.SearchFile.VerNum).First()).ToList();

        //        foreach (SearchFilesItemCodes itemFile in filteredList)
        //        {
        //            var file = itemFile.SearchFile;
        //            ACW.File latestFile = conn.WebServiceManager.DocumentService.GetLatestFileByMasterId(file.MasterId);

        //            Folder folder = conn.WebServiceManager.DocumentService.GetFolderById(latestFile.FolderId);

        //            //var localFolderPath = Path.Combine(folder.FullName, folder.Name);
        //            var localFolderPath = folder.FullName.Replace("$", "D:").Replace("/", "\\");

        //            string localFilePath = Path.Combine(localFolderPath, file.Name);
        //            var fileStream = vault.getFileStream(file);
        //            using var memoryStream = new MemoryStream();
        //            fileStream.CopyTo(memoryStream);
        //            byte[] fileBytes = memoryStream.ToArray();


        //            var item = new FileTransferItem
        //            {
        //                Path = localFilePath,
        //                Base64Content = Convert.ToBase64String(fileBytes)
        //            };

        //            result.Add(item);

        //            //// Generate a local file path (you can customize the naming convention)
        //            //string localFilePath = Path.Combine(_localDirectory, file.Name);

        //            //// Save the file contents to the local path
        //            //File.WriteAllBytes(localFilePath, fileContents);

        //            //// Add the local path to the list
        //            //localFilePaths.Add(localFilePath);
        //        }

        //        Console.WriteLine($"Total search files: {result.Count}");

        //        //var filterOutFile = totalResults.Where(file => file.Name.StartsWith("GLE004")).Take(1).ToList()[0];

        //        // Getting GetAssemblyAssociations of file
        //        // vault.GetAssemblyAssociations(filterOutFile.Id, conn.WebServiceManager.DocumentService);
        //        //return Ok(new { success = true, message = "Search complete. : " });
        //        return Ok(result);
        //    }
        //    catch (Exception ex)
        //    {
        //        return StatusCode(500, new { success = false, message = "Failed to checkout.", error = ex.Message });
        //    }

        //}

        [HttpPost("find")]
        public IActionResult findFilesByFileName([FromBody] BulkUploadRequest request)
        {
            try
            {

                if (request == null || request.Parts == null || !request.Parts.Any())
                    return BadRequest("Invalid data.");

                Console.WriteLine($"Received file: {request.FileName}");

                VaultConn vault = new();
                // Temporary getting static file name. 
                //string findFileName = "_CERIM-6.3KL";
                string fileName = request.FileName;
                string startName = "GLE";
                string extension = ".iam";
                Connection conn = vault.getConnectionObject();
                PropDef[] filePropDefs = conn.WebServiceManager.PropertyService.GetPropertyDefinitionsByEntityClassId("FILE");

                PropDef fileNamePropDefFirst = filePropDefs.Single(n => n.DispName == "File Name");
                PropDef fileNamePropDefSecond = filePropDefs.Single(n => n.DispName == "File Name");
                PropDef fileExtensionPropDef = filePropDefs.Single(n => n.DispName == "File Extension");

                SrchCond searchFileByNameProjectFirst = new SrchCond()
                {
                    PropDefId = fileNamePropDefFirst.Id,
                    PropTyp = PropertySearchType.SingleProperty,
                    SrchOper = 1, // 1 = contains, 7 = greater than or equal to
                    SrchRule = SearchRuleType.Must,
                    SrchTxt = fileName
                };

                SrchCond searchFileByNameProjectSecond = new SrchCond()
                {
                    PropDefId = fileNamePropDefSecond.Id,
                    PropTyp = PropertySearchType.SingleProperty,
                    SrchOper = 1, // 1 = contains, 7 = greater than or equal to
                    SrchRule = SearchRuleType.Must,
                    SrchTxt = startName
                };

                SrchCond searchFileByExtensionProject = new SrchCond()
                {
                    PropDefId = fileExtensionPropDef.Id,
                    PropTyp = PropertySearchType.SingleProperty,
                    SrchOper = 1, // 1 = contains, 7 = greater than or equal to
                    SrchRule = SearchRuleType.Must,
                    SrchTxt = extension
                };

                string bookmark = string.Empty;
                SrchStatus status = null;
                List<ACW.File> totalResults = new List<ACW.File>();

                while (status == null || totalResults.Count < status.TotalHits)
                {
                    ACW.File[] results = conn.WebServiceManager.DocumentService.FindFilesBySearchConditions(
                        new SrchCond[] { searchFileByNameProjectFirst, searchFileByNameProjectSecond, searchFileByExtensionProject },
                        null, null, false, true, ref bookmark, out status);

                    if (results != null)
                        totalResults.AddRange(results);
                    else
                        break;
                }
                var topFiles = totalResults.Where(file => file.Name.StartsWith("GLE004")).Take(5).ToList();

                var baseFolder = "D:\\Vault\\Designs\\ASSEMBLY\\SO NO";

                var localFilePaths = new List<string>();
                var result = new List<FileTransferItem>();

                foreach (var file in topFiles)
                {
                    ACW.File latestFile = conn.WebServiceManager.DocumentService.GetLatestFileByMasterId(file.MasterId);

                    Folder folder = conn.WebServiceManager.DocumentService.GetFolderById(latestFile.FolderId);

                    var localFolderPath = Path.Combine(baseFolder, folder.Name);

                    string localFilePath = Path.Combine(localFolderPath, file.Name);
                    var fileStream = vault.getFileStream(file);
                    using var memoryStream = new MemoryStream();
                    fileStream.CopyTo(memoryStream);
                    byte[] fileBytes = memoryStream.ToArray();


                    var item = new FileTransferItem
                    {
                        Path = localFilePath,
                        Base64Content = Convert.ToBase64String(fileBytes)
                    };

                    result.Add(item);

                    //// Generate a local file path (you can customize the naming convention)
                    //string localFilePath = Path.Combine(_localDirectory, file.Name);

                    //// Save the file contents to the local path
                    //File.WriteAllBytes(localFilePath, fileContents);

                    //// Add the local path to the list
                    //localFilePaths.Add(localFilePath);
                }

                //return localFilePaths.ToArray(); // Return the array of local file paths



                // Getting GetAssemblyAssociations of file
                //vault.GetAssemblyAssociations(filterOutFile.Id, conn.WebServiceManager.DocumentService);

                //var b = conn.WebServiceManager.DocumentService.ValidateBOMByFileId(filterOutFile.Id);
                //BOM bom = conn.WebServiceManager.DocumentService.GetBOMByFileId(filterOutFile.Id);

                //Item[] items = conn.WebServiceManager.ItemService.GetItemsByFileId(filterOutFile.Id);

                //ItemBOM bomRows = conn.WebServiceManager.ItemService.GetItemBOMByItemIdAndDate(
                //    items[0].Id, DateTime.Now, BOMTyp.Tip,
                //    BOMViewEditOptions.Defaults |
                //    BOMViewEditOptions.ReturnUnassignedComponents |
                //    BOMViewEditOptions.ReturnExcluded |
                //    BOMViewEditOptions.ReturnReferenceDesignators);

                //Console.WriteLine(bomRows);

                //var fileStream = vault.getFileStream(filterOutFile);

                //return File(fileStream, "application/octet-stream", filterOutFile.Name);
                return Ok(result);
                //return Ok(new { success = true, message = "Connected to Vault successfully. : " });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { success = false, message = "Failed to checkout.", error = ex.Message });
            }

        }

    }
}
