from cson_parser import parse_cson

def main():
    # Example 1: Simple CSON string
    simple_cson = '''
    title: "My First Note"
    content: "This is a simple note"
    tags: [
        "personal"
        "test"
    ]
    created: 2024.0413
    is_important: true
    '''
    
    print("Example 1 - Simple CSON:")
    result = parse_cson(simple_cson)
    print(result)
    print("\n")

    # Example 2: Nested CSON
    nested_cson = '''
    note: {
        metadata: {
            author: "John Doe"
            version: 1.0
        }
        content: {
            title: "Nested Note"
            body: "This is a note with nested structure"
            sections: [
                "Introduction"
                "Main Content"
                "Conclusion"
            ]
        }
    }
    '''
    
    print("Example 2 - Nested CSON:")
    result = parse_cson(nested_cson)
    print(result)

if __name__ == "__main__":
    main() 