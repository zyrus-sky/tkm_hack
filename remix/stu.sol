// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract CollegeAdmin {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    modifier onlyStudent(string calldata _college, address _student) {
        require(
            students[_college][_student].wallet != address(0),
            "Student does not exist"
        );
        require(msg.sender == _student || msg.sender == owner, "Not authorized");
        _;
    }

    struct Faculty {
        string name;
        string role;
        address wallet;
    }

    struct Student {
        string name;
        string rollNo;
        uint8 year;
        string department;
        string section;
        string email;
        address wallet;
    }

    struct StudentInput {
        string name;
        string rollNo;
        uint8 year;
        string department;
        string section;
        string email;
    }

    struct StudentGrades {
        string[] subjects;
        mapping(string => uint8) marks;
    }

    struct College {
        string name;
        address admin;
        string[] departments;
        mapping(string => address) departmentAdmins;
    }

    // Storage
    mapping(string => College) private colleges; // collegeName -> College
    mapping(string => mapping(string => mapping(address => Faculty))) private faculties; // college -> dept -> wallet -> Faculty
    mapping(string => mapping(address => Student)) private students; // college -> wallet -> Student
    mapping(string => mapping(address => StudentGrades)) private grades; // college -> wallet -> grades
    mapping(string => mapping(address => uint256)) private scholarships; // college -> wallet -> amount
    mapping(string => mapping(address => uint256)) private points; // college -> wallet -> points

    // Register College
    function registerCollege(string calldata _collegeName) external onlyOwner {
        require(bytes(colleges[_collegeName].name).length == 0, "Exists");
        colleges[_collegeName].name = _collegeName;
        colleges[_collegeName].admin = msg.sender;
    }

    // Add Department
    function addDepartment(
        string calldata _collegeName,
        string calldata _deptName,
        address _deptAdmin
    ) external onlyOwner {
        require(bytes(colleges[_collegeName].name).length > 0, "No college");
        colleges[_collegeName].departments.push(_deptName);
        colleges[_collegeName].departmentAdmins[_deptName] = _deptAdmin;
    }

    // Add Faculty
    function addFaculty(
        string calldata _collegeName,
        string calldata _deptName,
        Faculty calldata _faculty
    ) external onlyOwner {
        require(bytes(colleges[_collegeName].name).length > 0, "No college");
        faculties[_collegeName][_deptName][_faculty.wallet] = _faculty;
    }

    // Add Student
    function addStudent(
        string calldata _collegeName,
        address _wallet,
        StudentInput calldata _studentInput
    ) external onlyOwner {
        require(bytes(colleges[_collegeName].name).length > 0, "No college");
        students[_collegeName][_wallet] = Student({
            name: _studentInput.name,
            rollNo: _studentInput.rollNo,
            year: _studentInput.year,
            department: _studentInput.department,
            section: _studentInput.section,
            email: _studentInput.email,
            wallet: _wallet
        });
    }

    // Add or update marks
    function addMarks(
        string calldata _collegeName,
        address _student,
        string calldata _subject,
        uint8 _marks
    ) external onlyOwner {
        require(_marks <= 100, "Invalid marks");
        require(bytes(students[_collegeName][_student].name).length > 0, "No student");

        StudentGrades storage sg = grades[_collegeName][_student];

        bool exists = false;
        for (uint i = 0; i < sg.subjects.length; i++) {
            if (keccak256(bytes(sg.subjects[i])) == keccak256(bytes(_subject))) {
                exists = true;
                break;
            }
        }
        if (!exists) {
            sg.subjects.push(_subject);
        }
        sg.marks[_subject] = _marks;
    }

    // Get marks
    function getMarks(
        string calldata _collegeName,
        address _student
    ) external view returns (string[] memory, uint8[] memory) {
        StudentGrades storage sg = grades[_collegeName][_student];
        uint8[] memory marksList = new uint8[](sg.subjects.length);

        for (uint i = 0; i < sg.subjects.length; i++) {
            marksList[i] = sg.marks[sg.subjects[i]];
        }
        return (sg.subjects, marksList);
    }

    // Scholarship functions
    function setScholarship(string calldata _collegeName, address _student, uint256 _amount) external onlyOwner {
        scholarships[_collegeName][_student] = _amount;
    }

    function getScholarship(string calldata _collegeName, address _student) external view returns (uint256) {
        return scholarships[_collegeName][_student];
    }

    // Points functions
    function addPoints(string calldata _collegeName, address _student, uint256 _pts) external onlyOwner {
        points[_collegeName][_student] += _pts;
    }

    function getPoints(string calldata _collegeName, address _student) external view returns (uint256) {
        return points[_collegeName][_student];
    }

    function redeemPoints(string calldata _collegeName) external onlyStudent(_collegeName, msg.sender) {
        uint256 balance = points[_collegeName][msg.sender];
        require(balance > 0, "No points");
        points[_collegeName][msg.sender] = 0;
        emit PointsRedeemed(_collegeName, msg.sender, balance);
        // Add further logic to transfer rewards if needed
    }

    event PointsRedeemed(string college, address student, uint256 amount);

    // View functions
    function getStudent(string calldata _collegeName, address _student) external view returns (Student memory) {
        return students[_collegeName][_student];
    }

    function getDepartments(string calldata _collegeName) external view returns (string[] memory) {
        return colleges[_collegeName].departments;
    }

    function getFaculty(
        string calldata _collegeName,
        string calldata _deptName,
        address _facultyAddr
    ) external view returns (Faculty memory) {
        return faculties[_collegeName][_deptName][_facultyAddr];
    }
}
