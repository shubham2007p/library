
/*
 *  Tiny Library + Members  (CSV-style pipe-delimited text files)
 *  books.txt   : title|author|year
 *  members.txt : id|name|current_book_title   (empty if none issued)
 */
#include <stdio.h>
#include <string.h>
#include <ctype.h>

#define DB_BOOK   "books.txt"
#define DB_MEMBER "members.txt"
#define MAX       1024
#define MAXB      256
#define MAXM      256
#define FLEN      60

typedef struct {
    char title[FLEN];
    char author[FLEN];
    int  year;
} Book;

typedef struct {
    int  id;
    char name[FLEN];
    char current[FLEN];   /* title of issued book, empty if none */
} Member;

/* ---------- low-level helpers ---------- */
int load_books(Book *b) {
    FILE *f = fopen(DB_BOOK, "r");
    int n = 0;
    if (!f) return 0;
    while (n < MAXB &&
           fscanf(f, " %60[^|]|%60[^|]|%d\n", b[n].title, b[n].author, &b[n].year) == 3)
        ++n;
    fclose(f);
    return n;
}
void save_books(Book *b, int n) {
    FILE *f = fopen(DB_BOOK, "w");
    for (int i = 0; i < n; i++)
        fprintf(f, "%s|%s|%d\n", b[i].title, b[i].author, b[i].year);
    fclose(f);
}
int load_members(Member *m) {
    FILE *f = fopen(DB_MEMBER, "r");
    int n = 0;
    if (!f) return 0;
    while (n < MAXM &&
           fscanf(f, " %d|%60[^|]|%60[^\n]\n", &m[n].id, m[n].name, m[n].current) == 3)
        ++n;
    fclose(f);
    return n;
}
void save_members(Member *m, int n) {
    FILE *f = fopen(DB_MEMBER, "w");
    for (int i = 0; i < n; i++)
        fprintf(f, "%d|%s|%s\n", m[i].id, m[i].name, m[i].current);
    fclose(f);
}
void strip(char *s) {
    char *p = s, *q = s + strlen(s) - 1;
    while (isspace(*p)) p++;
    while (q > p && isspace(*q)) q--;
    q[1] = 0;
    memmove(s, p, strlen(p) + 1);
}

/* ---------- member actions ---------- */
void add_member(Member *m, int *nm) {
    if (*nm >= MAXM) { puts("Member DB full."); return; }
    printf("ID   : "); fflush(stdout);
    scanf("%d", &m[*nm].id); getchar();
    printf("Name : "); fflush(stdout);
    fgets(m[*nm].name, FLEN, stdin); strip(m[*nm].name);
    m[*nm].current[0] = 0;
    (*nm)++;
    save_members(m, *nm);
    puts("Member added.");
}
void list_members(Member *m, int nm) {
    if (!nm) { puts("No members."); return; }
    puts("\nID  Name                         Issued book");
    for (int i = 0; i < nm; i++)
        printf("%-3d %-28s %s\n", m[i].id, m[i].name,
               m[i].current[0] ? m[i].current : "-none-");
}

/* ---------- issue / return ---------- */
int find_member(Member *m, int nm, int id) {
    for (int i = 0; i < nm; i++) if (m[i].id == id) return i;
    return -1;
}
int find_book(Book *b, int nb, const char *title) {
    for (int i = 0; i < nb; i++) if (strcmp(b[i].title, title) == 0) return i;
    return -1;
}
void issue_book(Book *b, int nb, Member *m, int nm) {
    int id; char title[FLEN];
    printf("Member ID : "); fflush(stdout);
    scanf("%d", &id); getchar();
    int mi = find_member(m, nm, id);
    if (mi < 0) { puts("ID not found."); return; }
    if (m[mi].current[0]) { printf("Already has book: %s\n", m[mi].current); return; }
    printf("Book title: "); fflush(stdout);
    fgets(title, FLEN, stdin); strip(title);
    int bi = find_book(b, nb, title);
    if (bi < 0) { puts("Book not found."); return; }
    /* check not already issued */
    for (int i = 0; i < nm; i++)
        if (strcmp(m[i].current, title) == 0) {
            printf("Book already issued to %s\n", m[i].name); return;
        }
    strcpy(m[mi].current, title);
    save_members(m, nm);
    puts("Book issued.");
}
void return_book(Member *m, int nm) {
    int id;
    printf("Member ID returning: "); fflush(stdout);
    scanf("%d", &id); getchar();
    int mi = find_member(m, nm, id);
    if (mi < 0) { puts("ID not found."); return; }
    if (!m[mi].current[0]) { puts("No book to return."); return; }
    printf("Returned: %s\n", m[mi].current);
    m[mi].current[0] = 0;
    save_members(m, nm);
}

/* ---------- book actions ---------- */
void add_book(Book *b, int *nb) {
    if (*nb >= MAXB) { puts("Book DB full."); return; }
    printf("Title  : "); fflush(stdout);
    fgets(b[*nb].title, FLEN, stdin);  strip(b[*nb].title);
    printf("Author : "); fflush(stdout);
    fgets(b[*nb].author, FLEN, stdin); strip(b[*nb].author);
    printf("Year   : "); fflush(stdout);
    scanf("%d", &b[*nb].year); getchar();
    (*nb)++;
    save_books(b, *nb);
    puts("Book added.");
}
void list_books(Book *b, int nb) {
    if (!nb) { puts("No books."); return; }
    printf("\n%-35s %-25s %s\n", "TITLE", "AUTHOR", "YEAR");
    for (int i = 0; i < nb; i++)
        printf("%-35s %-25s %d\n", b[i].title, b[i].author, b[i].year);
}
void search_book(Book *b, int nb) {
    char key[FLEN];
    printf("Search (title substring): "); fflush(stdout);
    fgets(key, FLEN, stdin); strip(key);
    int found = 0;
    for (int i = 0; i < nb; i++)
        if (strstr(b[i].title, key)) {
            printf("%-35s %-25s %d\n", b[i].title, b[i].author, b[i].year);
            found = 1;
        }
    if (!found) puts("Not found.");
}
void delete_book(Book *b, int *nb, Member *m, int nm) {
    char key[FLEN];
    printf("Exact title to delete: "); fflush(stdout);
    fgets(key, FLEN, stdin); strip(key);
    /* refuse if anyone currently has it issued */
    for (int i = 0; i < nm; i++)
        if (strcmp(m[i].current, key) == 0) {
            printf("Cannot delete – currently issued to %s\n", m[i].name);
            return;
        }
    int j = 0;
    for (int i = 0; i < *nb; i++) {
        if (strcmp(b[i].title, key) == 0) { j++; continue; }
        if (j) b[i - j] = b[i];
    }
    if (j) {
        *nb -= j;
        save_books(b, *nb);
        printf("Deleted %d book(s).\n", j);
    } else {
        puts("Title not found – nothing deleted.");
    }
}

/* ---------- main menu ---------- */
int main(void) {
    Book shelf[MAXB]; int nb = load_books(shelf);
    Member mem[MAXM]; int nm = load_members(mem);
    int choice;
    for (;;) {
        puts("\n1)Add book 2)List books 3)Search 4)Delete");
        puts("5)Add member 6)List members 7)Issue 8)Return 0)Quit");
        printf("> "); fflush(stdout);
        if (scanf("%d", &choice) != 1) break; getchar();
        switch (choice) {
            case 1: add_book(shelf, &nb); break;
            case 2: list_books(shelf, nb); break;
            case 3: search_book(shelf, nb); break;
            case 4: delete_book(shelf, &nb, mem, nm); break;
            case 5: add_member(mem, &nm); break;
            case 6: list_members(mem, nm); break;
            case 7: issue_book(shelf, nb, mem, nm); break;
            case 8: return_book(mem, nm); break;
            case 0: return 0;
            default: puts("Invalid choice.");
        }
    }
    return 0;
}
