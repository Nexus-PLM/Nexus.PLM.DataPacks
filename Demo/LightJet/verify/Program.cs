// Opens a sealed .nexuscustomization with the Engine's own reader and reports what it found.
// The Python builder reproduces CanonicalJson's output by hand; this is the check that it
// actually does, rather than a package that only looks right until a site refuses it.

using System.Text.Json;
using Nexus.PLM.Services.CustomizationSets;

if (args.Length == 0)
{
    Console.Error.WriteLine("usage: VerifyPackage <package.nexuscustomization>");
    return 2;
}

var path = args[0];
if (!File.Exists(path))
{
    Console.Error.WriteLine($"No such file: {path}");
    return 2;
}

await using var stream = File.OpenRead(path);
var (package, report) = CustomizationPackage.Read(stream);

Console.WriteLine($"Package : {Path.GetFileName(path)}");
Console.WriteLine($"Valid   : {report.IsValid}");

if (package is not null)
{
    var m = package.Manifest;
    Console.WriteLine($"Name    : {m.Name} {m.Version}");
    Console.WriteLine($"Prefix  : {m.Source.CompanyPrefix}");
    Console.WriteLine($"Entries : {m.Entries.Count}");
    foreach (var (kind, count) in m.Contents.OrderBy(c => c.Key, StringComparer.Ordinal))
        Console.WriteLine($"  {kind,-16}{count}");

    // Every type file must parse and name a base that is either packaged or out of the box,
    // and no concrete type may grant canCreate - the first true flips the whole site to an
    // allowlist. Checking it here means a bad model cannot reach a site at all.
    var prefix = m.Source.CompanyPrefix;
    var packagedTypes = m.Entries.Where(e => e.Kind == PackageEntryKinds.Type)
                                 .Select(e => e.Key)
                                 .ToHashSet(StringComparer.OrdinalIgnoreCase);
    var problems = new List<string>();

    foreach (var entry in m.Entries.Where(e => e.Kind == PackageEntryKinds.Type))
    {
        using var doc = JsonDocument.Parse(package.Files[entry.Path]);
        var root = doc.RootElement;
        var typeName = root.GetProperty("typeName").GetString()!;
        var baseName = root.GetProperty("baseTypeName").GetString()!;
        var isAbstract = root.GetProperty("abstract").GetBoolean();

        if (prefix is not null && !typeName.StartsWith(prefix, StringComparison.Ordinal))
            problems.Add($"{typeName}: does not start with the package's declared " +
                         $"prefix '{prefix}'. A site refuses any type name that does not " +
                         "start with its own configured companyPrefix.");

        if (!packagedTypes.Contains(baseName) && !OotbBases.Contains(baseName))
            problems.Add($"{typeName}: base '{baseName}' is neither packaged nor out of the box.");

        if (!isAbstract && OotbBases.IsRoot(baseName))
            problems.Add($"{typeName}: concrete type derives straight off an out-of-the-box ROOT base; " +
                         "company attributes then have no shared home.");

        // A defaultValue must be a JSON string: the Engine reads it into a string?, and a
        // raw true or 42 throws and takes the whole type file with it.
        if (root.TryGetProperty("attributes", out var attrs))
        {
            foreach (var attr in attrs.EnumerateArray())
            {
                if (attr.TryGetProperty("defaultValue", out var dv) &&
                    dv.ValueKind is not (JsonValueKind.String or JsonValueKind.Null))
                {
                    problems.Add($"{typeName}.{attr.GetProperty("name").GetString()}: " +
                                 $"defaultValue is {dv.ValueKind}, must be a string.");
                }
            }
        }
    }

    // Until Services PR #798 this loop warned that ANY canCreate:true "flips creation to an
    // allowlist site-wide", because CanCreateAsync treated the right as opt-in: with no row
    // granting it, everyone had it. That read a policy backwards - a model denying create to
    // every subject of every type, as this one did, granted it to the whole site - and it is
    // now fixed, so the warning asserted the opposite of the truth and read as a reason to
    // abort the import.
    //
    // The useful check is the inverse. Create is deny-by-default for a type that carries a
    // security model at all, so a model with no granting row names nobody who may author that
    // type, and nobody but an administrator can. That is not a cautious default, it is a type
    // no role can use.
    foreach (var entry in m.Entries.Where(e => e.Kind == PackageEntryKinds.Security))
    {
        using var doc = JsonDocument.Parse(package.Files[entry.Path]);
        var rows = doc.RootElement.GetProperty("statePermissions").EnumerateArray().ToList();

        static bool Grants(JsonElement row) =>
            row.TryGetProperty("canCreate", out var cc) && cc.GetBoolean();

        if (!rows.Any(Grants))
            problems.Add($"{entry.Key}: no row grants canCreate, so only an administrator can create one.");

        foreach (var row in rows.Where(Grants))
        {
            var subjectType = row.TryGetProperty("subjectType", out var st) ? st.GetString() : null;
            if (subjectType == "*")
                problems.Add($"{entry.Key}: the wildcard row grants canCreate, so every signed-in user may create one.");
        }
    }

    Console.WriteLine(problems.Count == 0
        ? "Model   : structural checks passed"
        : $"Model   : {problems.Count} problem(s)");
    foreach (var problem in problems.Distinct())
        Console.WriteLine($"  ! {problem}");

    if (!report.IsValid || problems.Count > 0)
    {
        foreach (var error in report.Errors) Console.Error.WriteLine($"  ! {error}");
        return 1;
    }
}
else
{
    foreach (var error in report.Errors) Console.Error.WriteLine($"  ! {error}");
    return 1;
}

return 0;

static class OotbBases
{
    /// <summary>
    /// Out-of-the-box ROOT bases. A concrete type must not derive straight off one of
    /// these: the company's shared attributes would then have no type to live on, and every
    /// sibling would repeat them.
    /// </summary>
    private static readonly HashSet<string> Roots = new(StringComparer.OrdinalIgnoreCase)
    {
        "PLMCoreAbstractModel", "ItemsBase", "DocumentsBase", "FoldersBase", "FolderBase",
        "LinksBase", "RequirementsBase", "WorkItemBase", "IssueBase", "PersonBase",
        "ChangeBase", "MaterialBase", "TableBase", "IndustryStandardBase",
    };

    /// <summary>
    /// Out-of-the-box ABSTRACT LEAVES. Deriving a concrete type off one of these is correct
    /// and in several cases the only option: the requirement levels ship abstract, so a site
    /// that wants a requirements tree has no choice but to declare its own concrete type
    /// under each of them.
    /// </summary>
    private static readonly HashSet<string> AbstractLeaves = new(StringComparer.OrdinalIgnoreCase)
    {
        "MissionRequirement", "StakeholderRequirement", "SystemRequirement",
        "SubsystemRequirement", "ComponentRequirement", "BusinessRequirement",
        // A reference KIND is a type in this platform: ObjectReferenceLinkService
        // discovers every non-abstract descendant of ReferenceLinkBase from the registry,
        // so a site declares its own kinds by deriving from it and they appear in
        // GET .../references/kinds with no code change. It is abstract and registered out
        // of the box, and it was simply missing from this list - so the first package to
        // use the mechanism as designed was reported as naming an unknown base.
        "ReferenceLinkBase",
    };

    public static bool Contains(string name) => Roots.Contains(name) || AbstractLeaves.Contains(name);

    public static bool IsRoot(string name) => Roots.Contains(name);
}
