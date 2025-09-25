# book_journal

I want to build an app with you.

Sandwich menu:
	My books
	Add a book
	Statistics
	Settings
	
Add a book
	It's the first screen that opens by default as the app launches.
	There should be fields - any field can be hidden in settings, except for the Name.
	
  Button at the top: "Save" - saves the book, opens new blank "Add a book", shows notification if the book saved, shows error if the book hasn't been saved.
	
  Fields to fill in (empty by default if not stated otherwise, manual entry if not stated otherwise):
	Icon - choose one of preloaded icons, I should be able to add them later.
	DNF - toggle. False by default
	Name - first letters of each word are always capitalized
	Author - first letters of each word are always capitalized. Three best suited show up as the user types, for example: user writes "Ab", we show "Abercrombie", "Jimenez Abby", "Abraham Verghese".
	Size - choose one of: Short story — 4-30 pages, Novelette — 30-80 pages, Novella — 80-200 pages, Novel — 200-450 pages (set by default), Epic — 450+ pages.
	Category - choose one of: Fiction (set by default), Non-fiction 
	Genre - multiple choices. 
		for Category = Fiction choose from: literary, fantasy, science fiction, romance, mystery, crime, thriller, horror, historical, adventure, young adult;
		for Category = Non-fiction choose from: Biography, Memoir, History, Self-help, Personal development, Science, Popular science, Philosophy, Religion, Politics, Business, Economics, Travel writing, Essays, True crime, Guides
	
  Subgenre - multiple choices. Appears only for Category = Fiction, epties and disappears if Category changes to Non-fiction. If multiple Genre was chosen - show their Subgenre in one list.
		For Genre = Literary: Psychological fiction, Social commentary, Experimental/Avant-garde, Philosophical fiction, Stream of consciousness, Bildungsroman (coming-of-age), Metafiction;
		For Genre = Fantasy: High/Epic fantasy, Low fantasy, Urban fantasy, Dark fantasy, Sword & sorcery, Fairy tale retelling, Grimdark, Historical fantasy, Mythic fantasy, Portal fantasy;
		For Genre = Science Fiction: Hard sci-fi, Soft sci-fi, Space opera, Cyberpunk, Biopunk, Dystopian, Utopian, Time travel, Alternate history, Post-apocalyptic;
		For Genre = Romance: Contemporary romance, Historical romance, Regency romance, Paranormal romance, Fantasy romance, Romantic suspense, Erotica, Comedy romance (romcom), Inspirational romance, Gothic romance;
		For Genre = Mystery: Cozy mystery, Whodunit, Police procedural, Amateur sleuth, Locked-room mystery, Historical mystery, Noir mystery, Paranormal mystery;
		For Genre = Crime: Detective fiction, Noir / Hardboiled, Legal thriller, Mafia / Organized crime, Heist / Caper, Psychological crime, Domestic crime;
		For Genre = Thriller: Psychological thriller, Political thriller, Spy/Espionage, Techno-thriller, Legal thriller, Conspiracy thriller, Medical thriller; Action thriller, Eco-thriller;
		For Genre = Horror: Gothic horror, Supernatural horror, Psychological horror, Body horror, Splatterpunk, Cosmic horror, Folk horror, Survival horror;
		For Genre = Historical: Historical romance, Historical adventure, Historical mystery, Historical fantasy, Alternate history, War fiction, Biographical historical novels, Family sagas;
		For Genre = Adventure: Survival adventure, Swashbuckler, Quest adventure, Lost world adventure, Military adventure, Sea adventure, Pulp adventure, Exploration;
		For Genre = Young Adult (YA): Contemporary YA, Fantasy YA, Sci-Fi YA, Dystopian YA, Romance YA, Paranormal YA, Mystery/Thriller YA, Coming-of-age YA. 
	
  Source - multiple choices: E-book, Audiobook, Physical (mine), Physical (borrowed) 
	Where did I hear about it - multiple choices: Friend, Social media, Review, Store, Library, Other. And text field to enter manually. Table discovery
	My expectations
	Date started - calendar to choose the date
	Date finished - calendar to choose the date, today by default
	Rating - dots. 5 or 10 - depending on the settings which we add later. Stored in scale from 0 to 10. If settings changes it to 5, it renders like this: 1,2 out of 10 = 1 out of 5, 3,4 = 2, 5,6 = 3, 7,8 = 4, 9,10 = 5
	How different it is from my expectations
	Vibe - can be filled by hand (first letter capitalized) or picked from a list. The words the user entered before are added to the list. The list doesn't open on tap - only three best suited words show up as the user types, for example: user writes "bo", we show "boring", "bold", "bothering". The list will have to be able cleansed from user-added words later in settings. Always on the list: Dark, Gritty, Light, Epic, Intimate, Creepy, Playful, Witty, Passionate, Tragic, Melancholy, Hopeful, Optimistic, Cynical, Satirical, Tense, Fast-paced, Slow-burn, Chaotic, Wild, Cozy
	Character crush list
	Do I remember it three months later? - choose one of: Hell yes, Vaguely, Who??? - later we should be able to add notification when the date comes and highlight the book in "My books".
	Would I reread it? - choose one of: Absolutely, Maybe in crisis, Nah
	That line that got me
	What it reminded me of
	Do I need a physical copy? - choose one of: Yes, No
	Notes
	
  Button at the bottom: "Save" - saves the book
		if saved seccessfully, opens new blank "Add a book", scrolls to the top, shows notification (2 seconds) that the book saved
		if wasn't saved due to an error - shows the error (3 seconds).
			Possible errors:
				"Enter the Name" - if the Name is empty. Scrolls to the Name field, highlights it red.
				"Date started can't be later than Date finished" - if Date finished > Date started. Scrolls to the Date started field, highlights it red.

  The data should be stored locally in SQLite database and in a way that'll make it easy to export/import it - to transfer on another device for example.
	Also there should be left room for localisation later.
	The rest of it (My books, Statistics, Settings, Export, Import) will lead to placeholders for now.
	
Tables in database:
	books:
		id - autoincrement, int
		dnf - boolean
		name - text, required
		author - FK author.id
		size - FK size.id
		category - FK category.id
		genre - FK genre.id
		subgenre - FK subgenre.id
		source - FK source.id
		discovery - FK discovery.id
		discovery_text - text
		icon - FK icon.id
		expectations - text
		expectations_failed - text
		date_start - DATE
		date_finish - DATE
		rating - int
		crush_list - text
		months_later - FK months_later.id
		reread - FK reread.id
		line - text
		reminded - text
		phys_copy - boolean
		notes - text
		remember_check_due_at - DATE, books.date_finish + 90 days
	
  author:
		id - autoincrement, int
		author_name - text
		
  size:
		id - autoincrement, int
		size_name - 'Short story — 4-30 pages', 'Novelette — 30-80 pages', 'Novella — 80-200 pages', 'Novel — 200-450 pages', 'Epic — 450+ pages'.

  category:
		id - autoincrement, int
		category_name - 'Fiction', 'Non-fiction'

  genre:
		id - autoincrement, int
		category_id - category.id
		genre_name - text
		
    it's prefilled:
			for Category = Fiction: literary, fantasy, science fiction, romance, mystery, crime, thriller, horror, historical, adventure, young adult;
			for Category = Non-fiction: Biography, Memoir, History, Self-help, Personal development, Science, Popular science, Philosophy, Religion, Politics, Business, Economics, Travel writing, Essays, True crime, Guides
	
  subgenre:
		id - autoincrement, int
		genre_id - genre.id
		subgenre_name - text
		
		it's prefilled:
			For Genre = Literary: Psychological fiction, Social commentary, Experimental/Avant-garde, Philosophical fiction, Stream of consciousness, Bildungsroman (coming-of-age), Metafiction;
			For Genre = Fantasy: High/Epic fantasy, Low fantasy, Urban fantasy, Dark fantasy, Sword & sorcery, Fairy tale retelling, Grimdark, Historical fantasy, Mythic fantasy, Portal fantasy;
			For Genre = Science Fiction: Hard sci-fi, Soft sci-fi, Space opera, Cyberpunk, Biopunk, Dystopian, Utopian, Time travel, Alternate history, Post-apocalyptic;
			For Genre = Romance: Contemporary romance, Historical romance, Regency romance, Paranormal romance, Fantasy romance, Romantic suspense, Erotica, Comedy romance (romcom), Inspirational romance, Gothic romance;
			For Genre = Mystery: Cozy mystery, Whodunit, Police procedural, Amateur sleuth, Locked-room mystery, Historical mystery, Noir mystery, Paranormal mystery;
			For Genre = Crime: Detective fiction, Noir / Hardboiled, Legal thriller, Mafia / Organized crime, Heist / Caper, Psychological crime, Domestic crime;
			For Genre = Thriller: Psychological thriller, Political thriller, Spy/Espionage, Techno-thriller, Legal thriller, Conspiracy thriller, Medical thriller; Action thriller, Eco-thriller;
			For Genre = Horror: Gothic horror, Supernatural horror, Psychological horror, Body horror, Splatterpunk, Cosmic horror, Folk horror, Survival horror;
			For Genre = Historical: Historical romance, Historical adventure, Historical mystery, Historical fantasy, Alternate history, War fiction, Biographical historical novels, Family sagas;
			For Genre = Adventure: Survival adventure, Swashbuckler, Quest adventure, Lost world adventure, Military adventure, Sea adventure, Pulp adventure, Exploration;
			For Genre = Young Adult (YA): Contemporary YA, Fantasy YA, Sci-Fi YA, Dystopian YA, Romance YA, Paranormal YA, Mystery/Thriller YA, Coming-of-age YA. 
	
  source:
		id - autoincrement, int
		source - text, prefilled: 'E-book', 'Audiobook', 'Physical (mine)', 'Physical (borrowed)'
		
  discovery:
		id - autoincrement, int
		discovery_name - text, prefilled: Friend, Social media, Review, Store, Library, Other
	
  icon:
		id - autoincrement, int
		name - extracted from file name
		path - relative path, e.g. icons/fantasy_hat.png
		builtin - boolean
	
  vibe:
		id - autoincrement, int
		vibe_name - text, prefilled: Dark, Gritty, Light, Epic, Intimate, Creepy, Playful, Witty, Passionate, Tragic, Melancholy, Hopeful, Optimistic, Cynical, Satirical, Tense, Fast-paced, Slow-burn, Chaotic, Wild, Cozy
		prefilled - boolean. True for prefilled, false for added by user
		
  months_later:
		id - autoincrement, int
		name - prefilled: 'Hell yes', 'Vaguely', 'Who???'
		
  reread:
		id - autoincrement, int
		name - prefilled: Absolutely, Maybe in crisis, Nah
		
  settings (it's for toggling fields in "Add book" on and off):
		parameter_id - settings_options.id
		value - boolean
		
  settings_options:
		id - autoincrement, int
		name - prefilled: Icon, DNF, Author, Size, Category, Genre, Subgenre, Source, Where did I hear about it, My expectations, Date started, Date finished, Rating, How different it is from my expectations, Vibe, Character crush list, Do I remember it three months later?, Would I reread it?, That line that got me, What it reminded me of, Do I need a physical copy?, Notes, Rating_scale
		
My books
	Shows the list of books from table books. Each book shows:
		icon (if set, if not - empty),
		books.name,
		author.author_name (if set, if not - empty), Finished: date_finish (if set, if not - empty)
	
  The books with books.remember_check_due_at =< current system date - highlight it red.
	Tap on a book opens the book in the "Edit book"
	Filter button opens Filters:
		text field: searches in books.name, books.author, 
		DNF
		Size
		Category
		Genre
		Subgenre
		Source
		Where did I hear about it
		Date started - calendar to choose the date, range filter
		Date finished - calendar to choose the date, range filter
		Rating
		Vibe
		Do I remember it three months later?
		Would I reread it?
		Do I need a physical copy?
		Show rereads - shows the books with the same books.name
		
  "Order by" offer to order by (asc and desc):
		Date finished (default, desc)
		Date started
		Rating
		Name
		Author
	
"Edit book"
	UI is similar to "Add book". The difference is only "Save" button. If tapped, won't create new line in table books, but will update the opened one:
		if saved seccessfully, opens "My books", shows notification (2 seconds) that the book saved
		if wasn't saved due to an error - shows the error (3 seconds).
			Possible errors:
				"Enter the Name" - if the Name is empty. Scrolls to the Name field, highlights it red.
				"Date started can't be later than Date finished" - if Date finished > Date started. Scrolls to the Date started field, highlights it red.
				
Statistics
	Shows pie charts by:
		Rating: books.rating
		DNF: books.dnf
		Size of books: books.size
		Books category: books.category
		How I read my books: books.source
		How I find my books: books.heared
		How I remember my books: books.months_later
		Do I reread?: books.reread
		Do I need a physical copy?: books.phys_copy
	
  Shows lists:
		Genre: 5 most popular genres (the most books of the genre read. If there's less than 5 genres - show less).
		Subgenre: 10 most popular subgenres (the most books of the subgenre read. If there's less than 5 genres - show less).
		My vibe: 5 most popular vibes (the most chosen vibes. If there's less than 5 - show less).

Settings
	Language: ENG (by default), RU (does nothing for now - stays in English)
	Toggle fields in "Add a book":
		Icon
		DNF
		Author
		Size
		Category
		Genre
		Subgenre
		Source
		Where did I hear about it
		My expectations
		Date started
		Date finished
		Rating
		How different it is from my expectations
		Vibe
		Character crush list
		Do I remember it three months later?
		Would I reread it?
		That line that got me
		What it reminded me of
		Do I need a physical copy?
		Notes
	
  Rating - toggle between 5 score and 10. 10 = true, 5 = false
	
  Buttons:
	"Clear vibes" - clears user-added vibes. (vibe.prefilled = false)
	
  "Export" - exports data in JSON with schema_version
		if exported seccessfully, shows notification (2 seconds) that data is exported, stays in "Settings"
		if wasn't exported due to an error - shows the error (3 seconds).

  "Import" - offers to choose a JSON file to import. If file schema version mismatches - try to migrate
		if imported seccessfully, shows notification (2 seconds) that data is imported, stays in "Settings".
		if wasn't imported due to an error - shows the error (3 seconds).
		
  "Save" - saves settings
		if saved seccessfully, opens new blank "Add a book", scrolls to the top, shows notification (2 seconds) that settings saved
		if wasn't saved due to an error - shows the error (3 seconds).
