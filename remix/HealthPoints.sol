// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract HealthPortal {

    enum Role { NONE, ADMIN, STAFF }

    struct Staff {
        address eth;
        string name;
        string role;        // e.g. "Radiologist", "Gynecologist", etc.
        uint256 salary;     // salary in wei/month
        bool active;
    }

    struct HealthReport {
        address student;
        string cid;         // IPFS CID for medical report
        uint256 timestamp;
        uint256 points;     // karma points awarded
        bytes32 summaryHash; // hash of AI summary for verification
    }

    struct Hospital {
        string name;
        address admin;
        address[] staffAddresses;
        mapping(address => Staff) staff;
        HealthReport[] reports;
    }

    mapping(string => Hospital) private hospitals; // hospitalName => Hospital struct
    mapping(address => Role) public roles;         // quick lookup of user role

    // EVENTS
    event HospitalRegistered(string hospitalName, address indexed admin);
    event StaffAdded(string hospitalName, address indexed staffAddr, string staffName, string role);
    event SalaryUpdated(string hospitalName, address indexed staffAddr, uint256 newSalary);
    event HealthReportSubmitted(string hospitalName, address indexed staff, address indexed student, string cid, uint256 points);

    // Modifier for admin-only functions
    modifier onlyHospitalAdmin(string memory hospitalName) {
        require(hospitals[hospitalName].admin == msg.sender, "Only hospital admin can perform this");
        _;
    }

    // Modifier for staff-only functions
    modifier onlyHospitalStaff(string memory hospitalName) {
        require(hospitals[hospitalName].staff[msg.sender].active, "Only active hospital staff can perform this");
        _;
    }

    // Modifier to check hospital exists
    modifier hospitalExists(string memory hospitalName) {
        require(hospitals[hospitalName].admin != address(0), "Hospital not registered");
        _;
    }

    // Register a new hospital with msg.sender as admin
    function registerHospital(string calldata hospitalName) external {
        require(bytes(hospitalName).length > 0, "Hospital name required");
        require(hospitals[hospitalName].admin == address(0), "Hospital already exists");

        Hospital storage hosp = hospitals[hospitalName];
        hosp.name = hospitalName;
        hosp.admin = msg.sender;

        roles[msg.sender] = Role.ADMIN;

        emit HospitalRegistered(hospitalName, msg.sender);
    }

    // Add staff to a hospital by the hospital admin
    function addStaff(
        string calldata hospitalName,
        address staffEth,
        string calldata staffName,
        string calldata staffRole
    )
        external
        onlyHospitalAdmin(hospitalName)
        hospitalExists(hospitalName)
    {
        Hospital storage hosp = hospitals[hospitalName];
        require(staffEth != address(0), "Invalid staff address");
        require(hosp.staff[staffEth].eth == address(0), "Staff already exists");

        hosp.staff[staffEth] = Staff({
            eth: staffEth,
            name: staffName,
            role: staffRole,
            salary: 0,
            active: true
        });
        hosp.staffAddresses.push(staffEth);
        roles[staffEth] = Role.STAFF;

        emit StaffAdded(hospitalName, staffEth, staffName, staffRole);
    }

    // Set or update salary for staff by hospital admin
    function setSalary(
        string calldata hospitalName,
        address staffEth,
        uint256 salaryInWei
    )
        external
        onlyHospitalAdmin(hospitalName)
        hospitalExists(hospitalName)
    {
        Hospital storage hosp = hospitals[hospitalName];
        require(hosp.staff[staffEth].active, "Staff is not active");

        hosp.staff[staffEth].salary = salaryInWei;

        emit SalaryUpdated(hospitalName, staffEth, salaryInWei);
    }

    // Submit a health report by hospital staff
    function submitHealthReport(
        string calldata hospitalName,
        address student,
        string calldata cid,
        uint256 points,
        bytes32 summaryHash
    )
        external
        onlyHospitalStaff(hospitalName)
        hospitalExists(hospitalName)
    {
        require(student != address(0), "Invalid student address");

        hospitals[hospitalName].reports.push(HealthReport({
            student: student,
            cid: cid,
            timestamp: block.timestamp,
            points: points,
            summaryHash: summaryHash
        }));

        emit HealthReportSubmitted(hospitalName, msg.sender, student, cid, points);
    }

    // Get list of staff for a hospital with details
    function getStaffList(string calldata hospitalName) external view hospitalExists(hospitalName) returns (
        address[] memory staffAddresses,
        string[] memory names,
        string[] memory rolesArr,
        uint256[] memory salaries,
        bool[] memory activeFlags
    ) {
        Hospital storage hosp = hospitals[hospitalName];
        uint256 count = hosp.staffAddresses.length;

        staffAddresses = new address[](count);
        names = new string[](count);
        rolesArr = new string[](count);
        salaries = new uint256[](count);
        activeFlags = new bool[](count);

        for (uint256 i = 0; i < count; i++) {
            address addr = hosp.staffAddresses[i];
            Staff storage s = hosp.staff[addr];
            staffAddresses[i] = s.eth;
            names[i] = s.name;
            rolesArr[i] = s.role;
            salaries[i] = s.salary;
            activeFlags[i] = s.active;
        }
    }

    // Get all health reports submitted for a hospital
    function getAllReports(string calldata hospitalName) external view hospitalExists(hospitalName) returns (HealthReport[] memory) {
        return hospitals[hospitalName].reports;
    }

    // Get salary of a specific staff in a hospital
    function getSalary(string calldata hospitalName, address staffEth) external view hospitalExists(hospitalName) returns (uint256) {
        return hospitals[hospitalName].staff[staffEth].salary;
    }

    // Check if an address is the admin of a hospital
    function isAdmin(string calldata hospitalName, address user) external view hospitalExists(hospitalName) returns (bool) {
        return hospitals[hospitalName].admin == user;
    }
}
