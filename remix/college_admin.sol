// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CollegeAdmin {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized, owner only");
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

    struct StudentGrades {
        string[] subjects;
        mapping(string => uint8) subjectMarks;
    }

    struct College {
        string name;
        address admin;
        string[] departments;
        mapping(string => address) departmentAdmins;
    }

    // Storage mappings
    mapping(string => College) private colleges;
    mapping(string => mapping(string => mapping(address => Faculty))) private faculties;
    mapping(string => mapping(address => Student)) private students;
    mapping(string => mapping(address => StudentGrades)) private grades;

    // Grouped struct for Student input parameters
    struct StudentInput {
        string name;
        string rollNo;
        uint8 year;
        string department;
        string section;
        string email;
    }

    // Register a new college
    function registerCollege(string calldata _collegeName) external onlyOwner {
        require(bytes(colleges[_collegeName].name).length == 0, "College exists");
        colleges[_collegeName].name = _collegeName;
        colleges[_collegeName].admin = msg.sender;
    }

    // Add a department to a college
    function addDepartment(
        string calldata _collegeName,
        string calldata _deptName,
        address _deptAdmin
    ) external onlyOwner {
        require(bytes(colleges[_collegeName].name).length > 0, "College does not exist");
        colleges[_collegeName].departments.push(_deptName);
        colleges[_collegeName].departmentAdmins[_deptName] = _deptAdmin;
    }

    // Add faculty - reduces parameters (group if needed)
    function addFaculty(
        string calldata _collegeName,
        string calldata _deptName,
        Faculty calldata _faculty
    ) external onlyOwner {
        require(bytes(colleges[_collegeName].name).length > 0, "College does not exist");

        faculties[_collegeName][_deptName][_faculty.wallet] = Faculty({
            name: _faculty.name,
            role: _faculty.role,
            wallet: _faculty.wallet
        });
    }

    // Add a student using grouped parameters
    function addStudent(
        string calldata _collegeName,
        address _wallet,
        StudentInput calldata _studentInput
    ) external onlyOwner {
        require(bytes(colleges[_collegeName].name).length > 0, "College does not exist");

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

    // Add or update marks for a student
    function addMarks(
        string calldata _collegeName,
        address _student,
        string calldata _subject,
        uint8 _marks
    ) external onlyOwner {
        require(_marks <= 100, "Marks out of range");
        require(bytes(students[_collegeName][_student].name).length > 0, "Student does not exist");

        StudentGrades storage sg = grades[_collegeName][_student];

        bool subjectExists = false;
        for (uint i = 0; i < sg.subjects.length; i++) {
            if (keccak256(bytes(sg.subjects[i])) == keccak256(bytes(_subject))) {
                subjectExists = true;
                break;
            }
        }

        if (!subjectExists) {
            sg.subjects.push(_subject);
        }
        sg.subjectMarks[_subject] = _marks;
    }

    // Get subjects and marks for a student
    function getMarks(
        string calldata _collegeName,
        address _student
    ) external view returns (string[] memory, uint8[] memory) {
        StudentGrades storage sg = grades[_collegeName][_student];
        uint8[] memory marksList = new uint8[](sg.subjects.length);
        for (uint i = 0; i < sg.subjects.length; i++) {
            marksList[i] = sg.subjectMarks[sg.subjects[i]];
        }
        return (sg.subjects, marksList);
    }

    // Additional getters

    function getDepartments(string calldata _collegeName)
        external
        view
        returns (string[] memory)
    {
        return colleges[_collegeName].departments;
    }

    function getFaculty(
        string calldata _collegeName,
        string calldata _deptName,
        address _facultyAddr
    ) external view returns (Faculty memory) {
        return faculties[_collegeName][_deptName][_facultyAddr];
    }

    function getStudent(string calldata _collegeName, address _student)
        external
        view
        returns (Student memory)
    {
        return students[_collegeName][_student];
    }
}
