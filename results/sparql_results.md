# Αποτελέσματα ερωτημάτων SPARQL

Παράγεται από το `scripts/run_queries.py`. Για κάθε ερώτημα δίνεται το πλήθος γραμμών στην asserted οντολογία και στην οντολογία με τα συμπεράσματα του reasoner.

| Ερώτημα | Γράφημα | Γραμμές (asserted) | Γραμμές (inferred) |
|---|---|---:|---:|
| q01_package_catalogue | asserted | 8 | 8 |
| q02_flight_packages_under_1000 | asserted | 5 | 5 |
| q03_revenue_per_package | asserted | 6 | 6 |
| q04_best_rated_packages | asserted | 4 | 4 |
| q05_staff_contacts_union | asserted | 3 | 3 |
| q06_promoted_without_sales | asserted | 1 | 1 |
| q07_outstanding_balance | asserted | 11 | 11 |
| q08_vip_customers_reasoning | inferred | 0 | 4 |
| q09_packages_per_country_reasoning | inferred | 0 | 3 |
| q10_package_categories_reasoning | inferred | 7 | 7 |
| q11_hotels_in_greece_reasoning | inferred | 0 | 4 |

## Q1. Κατάλογος πακέτων διακοπών: προορισμός, διάρκεια και τιμή ανά άτομο,

Αρχείο: `queries/q01_package_catalogue.rq` — γράφημα: **asserted** (asserted: 8 γραμμές, inferred: 8 γραμμές)

| package | destination | days | price |
|---|---|---|---|
| Thessaloniki Gastronomy Weekend | Θεσσαλονίκη | 2 | 230 |
| Arachova Winter Weekend | Αράχωβα | 3 | 310 |
| Paris City Break | Παρίσι | 3 | 560 |
| Mykonos Summer | Μύκονος | 5 | 640 |
| Roman Holiday | Ρώμη | 4 | 720 |
| Santorini Escape | Σαντορίνη | 7 | 890 |
| Cyclades Island Hopping | Μύκονος | 10 | 1450 |
| Cyclades Island Hopping | Σαντορίνη | 10 | 1450 |

## Q2. Πακέτα με πτήση και τιμή κάτω από 1000 €, με αριθμό πτήσης και αεροπορική

Αρχείο: `queries/q02_flight_packages_under_1000.rq` — γράφημα: **asserted** (asserted: 5 γραμμές, inferred: 5 γραμμές)

| package | price | flight | airline | excursion | guide |
|---|---|---|---|---|---|
| Paris City Break | 560 | MS440 | MedSky Airways | Ξενάγηση στο Λούβρο |  |
| Roman Holiday | 720 | MS330 | MedSky Airways | Ξενάγηση στα Μουσεία του Βατικανού | Γιώργος Νικολάου |
| Roman Holiday | 720 | MS331 | MedSky Airways | Ξενάγηση στα Μουσεία του Βατικανού | Γιώργος Νικολάου |
| Santorini Escape | 890 | HA101 | HellasAir | Κρουαζιέρα στο ηφαίστειο | Σοφία Αλεξίου |
| Santorini Escape | 890 | HA102 | HellasAir | Κρουαζιέρα στο ηφαίστειο | Σοφία Αλεξίου |

## Q3. Επιβεβαιωμένες κρατήσεις, ταξιδιώτες και έσοδα ανά πακέτο, από τα πιο

Αρχείο: `queries/q03_revenue_per_package.rq` — γράφημα: **asserted** (asserted: 6 γραμμές, inferred: 6 γραμμές)

| package | bookings | travellers | revenue |
|---|---|---|---|
| Cyclades Island Hopping | 1 | 2 | 2900 |
| Mykonos Summer | 2 | 4 | 2560 |
| Roman Holiday | 2 | 3 | 2160 |
| Arachova Winter Weekend | 2 | 6 | 1860 |
| Santorini Escape | 1 | 2 | 1780 |
| Thessaloniki Gastronomy Weekend | 1 | 2 | 460 |

## Q4. Μέση βαθμολογία πελατών ανά πακέτο· εμφανίζονται μόνο τα πακέτα με μέσο

Αρχείο: `queries/q04_best_rated_packages.rq` — γράφημα: **asserted** (asserted: 4 γραμμές, inferred: 4 γραμμές)

| package | reviews | avgRating | worst |
|---|---|---|---|
| Cyclades Island Hopping | 1 | 5 | 5 |
| Santorini Escape | 1 | 5 | 5 |
| Thessaloniki Gastronomy Weekend | 1 | 5 | 5 |
| Arachova Winter Weekend | 1 | 4 | 4 |

## Q5. Με ποια μέλη του προσωπικού ήρθε σε επαφή ο πελάτης Πέτρος Μιχαήλ: οι

Αρχείο: `queries/q05_staff_contacts_union.rq` — γράφημα: **asserted** (asserted: 3 γραμμές, inferred: 3 γραμμές)

| role | employee | context |
|---|---|---|
| Οδηγός / Συνοδός | Γιώργος Νικολάου | Roman Holiday: Ξενάγηση στα Μουσεία του Βατικανού |
| Ταξιδιωτικός σύμβουλος | Μαρία Παπαδοπούλου | Cyclades Island Hopping |
| Ταξιδιωτικός σύμβουλος | Νίκος Γεωργίου | Roman Holiday |

## Q6. Πακέτα που προβάλλονται σε διαφημιστική καμπάνια αλλά δεν έχουν ακόμη

Αρχείο: `queries/q06_promoted_without_sales.rq` — γράφημα: **asserted** (asserted: 1 γραμμές, inferred: 1 γραμμές)

| package | campaign | budget | channels |
|---|---|---|---|
| Paris City Break | City breaks στην Ευρώπη | 3500 | Social media (Facebook / Instagram), Ραδιοφωνικό σποτ |

## Q7. Έλεγχος εξόφλησης: για κάθε μη ακυρωμένη κράτηση υπολογίζεται το κόστος

Αρχείο: `queries/q07_outstanding_balance.rq` — γράφημα: **asserted** (asserted: 11 γραμμές, inferred: 11 γραμμές)

| booking | customer | package | status | cost | paid | balance |
|---|---|---|---|---|---|---|
| Booking10 | Καρρά | Santorini Escape | Σε αναμονή | 890 | 0 | 890 |
| Booking06 | Σταύρου | Paris City Break | Σε αναμονή | 560 | 0 | 560 |
| Booking01 | Καρράς | Santorini Escape | Επιβεβαιωμένη | 1780 | 1780 | 0 |
| Booking02 | Λαζάρου | Mykonos Summer | Επιβεβαιωμένη | 640 | 640 | 0 |
| Booking03 | Μιχαήλ | Cyclades Island Hopping | Επιβεβαιωμένη | 2900 | 2900 | 0 |
| Booking04 | Μιχαήλ | Roman Holiday | Επιβεβαιωμένη | 720 | 720 | 0 |
| Booking05 | Smith | Roman Holiday | Επιβεβαιωμένη | 1440 | 1440 | 0 |
| Booking07 | Παππάς | Arachova Winter Weekend | Επιβεβαιωμένη | 1240 | 1240 | 0 |
| Booking09 | Κώστα | Thessaloniki Gastronomy Weekend | Επιβεβαιωμένη | 460 | 460 | 0 |
| Booking11 | Κώστα | Mykonos Summer | Επιβεβαιωμένη | 1920 | 1920 | 0 |
| Booking12 | Καρράς | Arachova Winter Weekend | Επιβεβαιωμένη | 620 | 620 | 0 |

## Q8. [Reasoning] Οι πελάτες VIP και οι σύμβουλοι που τους εξυπηρέτησαν.

Αρχείο: `queries/q08_vip_customers_reasoning.rq` — γράφημα: **inferred** (asserted: 0 γραμμές, inferred: 4 γραμμές)

| customer | points | servedBy |
|---|---|---|
| Πέτρος Μιχαήλ | 2600 | Παπαδοπούλου, Γεωργίου |
| Δημήτρης Καρράς | 1850 | Γεωργίου, Δημητρίου |
| Μάρθα Κώστα | 1200 | Δημητρίου, Γεωργίου |
| John Smith | 1000 | Γεωργίου |

## Q9. [Reasoning] Πόσα πακέτα επισκέπτονται κάθε χώρα. Τα πακέτα συνδέονται μόνο με

Αρχείο: `queries/q09_packages_per_country_reasoning.rq` — γράφημα: **inferred** (asserted: 0 γραμμές, inferred: 3 γραμμές)

| country | packages | packageNames |
|---|---|---|
| Ελλάδα | 5 | Thessaloniki Gastronomy Weekend, Mykonos Summer, Cyclades Island Hopping, Arachova Winter Weekend, Santorini Escape |
| Γαλλία | 1 | Paris City Break |
| Ιταλία | 1 | Roman Holiday |

## Q10. [Reasoning] Σε ποιες ορισμένες (defined) κατηγορίες ανήκει κάθε πακέτο.

Αρχείο: `queries/q10_package_categories_reasoning.rq` — γράφημα: **inferred** (asserted: 7 γραμμές, inferred: 7 γραμμές)

| package | categories |
|---|---|
| Arachova Winter Weekend |  |
| Cyclades Island Hopping | Πακέτο με Πτήση, Νησιωτικό Πακέτο, Πακέτο Μεγάλης Διάρκειας |
| Mykonos Summer | Νησιωτικό Πακέτο, Πακέτο με Συνοδό |
| Paris City Break | Πακέτο με Πτήση, Πακέτο με Συνοδό |
| Roman Holiday | Πακέτο με Πτήση, Πακέτο με Συνοδό |
| Santorini Escape | Πακέτο με Πτήση, Νησιωτικό Πακέτο, Πακέτο με Συνοδό, Πακέτο Μεγάλης Διάρκειας |
| Thessaloniki Gastronomy Weekend | Πακέτο με Συνοδό |

## Q11. [Reasoning] Ξενοδοχεία στην Ελλάδα, με κατηγορία αστέρων και προορισμό. Κάθε

Αρχείο: `queries/q11_hotels_in_greece_reasoning.rq` — γράφημα: **inferred** (asserted: 0 γραμμές, inferred: 4 γραμμές)

| hotel | stars | destination |
|---|---|---|
| Caldera View Hotel | 5 | Σαντορίνη |
| Mykonos Blue Suites | 4 | Μύκονος |
| Parnassos Chalet | 4 | Αράχωβα |
| White Tower Hotel | 3 | Θεσσαλονίκη |

