    export const fixedHeaders = [ // Headers that are always present
        "Id",
        "Researchers",
        "Org",
        "Promoter",
        "Total Load",
        "Load Q1",
        "Load Q2",
    ];
    export const fixedRowsText = [ // Rows that are always present
        "Id",
        "Quadri",
        "Acads",
        "Nbr Students",
        "Assistant",
        "Total for now",
    ];

    export const ColumnIndices = { // Indices of the columns in the table
        ID: 0,
        RESEARCHERS: 1,
        ORG: 2,
        PROMOTER: 3,
        TOTAL_LOAD: 4,
        LOAD_Q1: 5,
        LOAD_Q2: 6,
    };
    export const RowIndices = { // Information indexes in the table for rows
        ID: 0,
        QUADRI: 1,
        ACADS: 2,
        NBR_STUDENTS: 3,
        ASSISTANTS: 4,
        TOTAL_ASSISTANT_NOW: 5,
    };

    export const lenFixedRowsText = fixedRowsText.length; // Number of fixed rows
    export const lenFixedHeaders = fixedHeaders.length; // Number of fixed headers
    export  const borderStyle = {width: 2, color: 'black'}; // Border style for the table

    export const requiredProperties = ['id', 'quadri', 'assigned_teachers', 'nbr_students', 'nbr_teaching_assistants']; // Required properties for the table

    export const taLoad = 4; // Load of a teaching assistant
    export const phdLoad = 2; // Load of a phd student
    export const postDocLoad = 1; // Load of a post doc