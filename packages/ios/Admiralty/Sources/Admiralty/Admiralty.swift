// Generated from admiralty-symbols.json (Admiralty 0.400). Do not edit by hand.
// Licensed under the SIL Open Font License 1.1 (see OFL.txt).

import SwiftUI
import CoreText
#if canImport(UIKit)
import UIKit
#endif

/// All 282 Admiralty Symbols. The raw value is the symbol's name, as in the
/// SVG files and the inspector: `AdmiraltySymbol(rawValue: "heart-filled")`.
public enum AdmiraltySymbol: String, CaseIterable, Sendable {
    case send = "send"
    case stop = "stop"
    case mic = "mic"
    case micOff = "mic-off"
    case attach = "attach"
    case image = "image"
    case camera = "camera"
    case copy = "copy"
    case paste = "paste"
    case cut = "cut"
    case retry = "retry"
    case regenerate = "regenerate"
    case edit = "edit"
    case delete = "delete"
    case reply = "reply"
    case forwardMessage = "forward-message"
    case quote = "quote"
    case pin = "pin"
    case unpin = "unpin"
    case mention = "mention"
    case emoji = "emoji"
    case thumbsUp = "thumbs-up"
    case thumbsDown = "thumbs-down"
    case voiceMessage = "voice-message"
    case agent = "agent"
    case user = "user"
    case team = "team"
    case tool = "tool"
    case plug = "plug"
    case memory = "memory"
    case taskList = "task-list"
    case reminder = "reminder"
    case sparkle = "sparkle"
    case plan = "plan"
    case workflow = "workflow"
    case automation = "automation"
    case trigger = "trigger"
    case approval = "approval"
    case permission = "permission"
    case handoff = "handoff"
    case skill = "skill"
    case knowledge = "knowledge"
    case context = "context"
    case source = "source"
    case citation = "citation"
    case prompt = "prompt"
    case model = "model"
    case backgroundTask = "background-task"
    case back = "back"
    case forward = "forward"
    case up = "up"
    case down = "down"
    case chevronLeft = "chevron-left"
    case chevronRight = "chevron-right"
    case chevronUp = "chevron-up"
    case chevronDown = "chevron-down"
    case arrowUpRight = "arrow-up-right"
    case arrowDownLeft = "arrow-down-left"
    case arrowUpLeft = "arrow-up-left"
    case arrowDownRight = "arrow-down-right"
    case doubleChevronLeft = "double-chevron-left"
    case doubleChevronRight = "double-chevron-right"
    case expand = "expand"
    case collapse = "collapse"
    case fullscreen = "fullscreen"
    case exitFullscreen = "exit-fullscreen"
    case home = "home"
    case menu = "menu"
    case moreHorizontal = "more-horizontal"
    case moreVertical = "more-vertical"
    case close = "close"
    case sidebarLeft = "sidebar-left"
    case sidebarRight = "sidebar-right"
    case grid = "grid"
    case list = "list"
    case dashboard = "dashboard"
    case tabs = "tabs"
    case window = "window"
    case newWindow = "new-window"
    case splitView = "split-view"
    case check = "check"
    case checkCircle = "check-circle"
    case info = "info"
    case warning = "warning"
    case error = "error"
    case help = "help"
    case loading = "loading"
    case progress = "progress"
    case offline = "offline"
    case online = "online"
    case sync = "sync"
    case verified = "verified"
    case new = "new"
    case beta = "beta"
    case badge = "badge"
    case notificationDot = "notification-dot"
    case pending = "pending"
    case timeout = "timeout"
    case bell = "bell"
    case file = "file"
    case newFile = "new-file"
    case folder = "folder"
    case newFolder = "new-folder"
    case document = "document"
    case spreadsheet = "spreadsheet"
    case presentation = "presentation"
    case pdf = "pdf"
    case imageFile = "image-file"
    case audioFile = "audio-file"
    case videoFile = "video-file"
    case codeFile = "code-file"
    case archive = "archive"
    case link = "link"
    case unlink = "unlink"
    case share = "share"
    case export = "export"
    case `import` = "import"
    case download = "download"
    case upload = "upload"
    case bookmark = "bookmark"
    case tag = "tag"
    case star = "star"
    case note = "note"
    case clipboard = "clipboard"
    case trash = "trash"
    case restore = "restore"
    case history = "history"
    case version = "version"
    case compare = "compare"
    case template = "template"
    case print = "print"
    case save = "save"
    case duplicate = "duplicate"
    case rename = "rename"
    case label = "label"
    case search = "search"
    case zoomIn = "zoom-in"
    case zoomOut = "zoom-out"
    case filter = "filter"
    case sort = "sort"
    case sortAscending = "sort-ascending"
    case sortDescending = "sort-descending"
    case findInPage = "find-in-page"
    case recent = "recent"
    case savedSearch = "saved-search"
    case advancedSearch = "advanced-search"
    case clear = "clear"
    case settings = "settings"
    case sliders = "sliders"
    case toggleOn = "toggle-on"
    case toggleOff = "toggle-off"
    case theme = "theme"
    case darkMode = "dark-mode"
    case lightMode = "light-mode"
    case autoMode = "auto-mode"
    case fontSize = "font-size"
    case language = "language"
    case accessibility = "accessibility"
    case notificationSettings = "notification-settings"
    case privacySettings = "privacy-settings"
    case dataControls = "data-controls"
    case profile = "profile"
    case account = "account"
    case lock = "lock"
    case unlock = "unlock"
    case key = "key"
    case passkey = "passkey"
    case password = "password"
    case shieldCheck = "shield-check"
    case shieldAlert = "shield-alert"
    case eye = "eye"
    case eyeOff = "eye-off"
    case incognito = "incognito"
    case encryption = "encryption"
    case consent = "consent"
    case auditLog = "audit-log"
    case block = "block"
    case reportFlag = "report-flag"
    case twoFactor = "two-factor"
    case cloud = "cloud"
    case cloudUpload = "cloud-upload"
    case cloudDownload = "cloud-download"
    case cloudOff = "cloud-off"
    case backup = "backup"
    case restoreBackup = "restore-backup"
    case syncNow = "sync-now"
    case autoSync = "auto-sync"
    case syncPaused = "sync-paused"
    case syncError = "sync-error"
    case signIn = "sign-in"
    case signOut = "sign-out"
    case switchAccount = "switch-account"
    case addAccount = "add-account"
    case upgrade = "upgrade"
    case helpCenter = "help-center"
    case feedback = "feedback"
    case support = "support"
    case reportAProblem = "report-a-problem"
    case about = "about"
    case whatsNew = "whats-new"
    case tutorial = "tutorial"
    case tips = "tips"
    case shareApp = "share-app"
    case rateApp = "rate-app"
    case legal = "legal"
    case code = "code"
    case terminal = "terminal"
    case codeBlock = "code-block"
    case runCode = "run-code"
    case branch = "branch"
    case starFilled = "star-filled"
    case bookmarkFilled = "bookmark-filled"
    case pinFilled = "pin-filled"
    case thumbsUpFilled = "thumbs-up-filled"
    case thumbsDownFilled = "thumbs-down-filled"
    case bellFilled = "bell-filled"
    case micFilled = "mic-filled"
    case stopFilled = "stop-filled"
    case computer = "computer"
    case laptop = "laptop"
    case phone = "phone"
    case tablet = "tablet"
    case watch = "watch"
    case devices = "devices"
    case browser = "browser"
    case brain = "brain"
    case webSearch = "web-search"
    case deepResearch = "deep-research"
    case project = "project"
    case artifact = "artifact"
    case summarize = "summarize"
    case translate = "translate"
    case computerUse = "computer-use"
    case screenShare = "screen-share"
    case `extension` = "extension"
    case api = "api"
    case server = "server"
    case chat = "chat"
    case newChat = "new-chat"
    case conversations = "conversations"
    case editMessage = "edit-message"
    case readReceipt = "read-receipt"
    case scheduleSend = "schedule-send"
    case hashtag = "hashtag"
    case keyboard = "keyboard"
    case command = "command"
    case usage = "usage"
    case appearance = "appearance"
    case billing = "billing"
    case receipt = "receipt"
    case wallet = "wallet"
    case subscription = "subscription"
    case faceId = "face-id"
    case fingerprint = "fingerprint"
    case qrCode = "qr-code"
    case scan = "scan"
    case calendar = "calendar"
    case scheduledTask = "scheduled-task"
    case timer = "timer"
    case location = "location"
    case map = "map"
    case play = "play"
    case pause = "pause"
    case volume = "volume"
    case mute = "mute"
    case headphones = "headphones"
    case readAloud = "read-aloud"
    case subtitles = "subtitles"
    case record = "record"
    case barChart = "bar-chart"
    case lineChart = "line-chart"
    case pieChart = "pie-chart"
    case trendingUp = "trending-up"
    case mail = "mail"
    case inbox = "inbox"
    case phoneCall = "phone-call"
    case contacts = "contacts"
    case dragHandle = "drag-handle"
    case heart = "heart"
    case bug = "bug"
    case heartFilled = "heart-filled"
    case playFilled = "play-filled"

    /// The Private Use Area code point of the symbol in the Admiralty Symbols font.
    public var codepoint: UInt32 {
        switch self {
        case .send: return 0xE000
        case .stop: return 0xE001
        case .mic: return 0xE002
        case .micOff: return 0xE003
        case .attach: return 0xE004
        case .image: return 0xE005
        case .camera: return 0xE006
        case .copy: return 0xE007
        case .paste: return 0xE008
        case .cut: return 0xE009
        case .retry: return 0xE00A
        case .regenerate: return 0xE00B
        case .edit: return 0xE00C
        case .delete: return 0xE00D
        case .reply: return 0xE00E
        case .forwardMessage: return 0xE00F
        case .quote: return 0xE010
        case .pin: return 0xE011
        case .unpin: return 0xE012
        case .mention: return 0xE013
        case .emoji: return 0xE014
        case .thumbsUp: return 0xE015
        case .thumbsDown: return 0xE016
        case .voiceMessage: return 0xE017
        case .agent: return 0xE018
        case .user: return 0xE019
        case .team: return 0xE01A
        case .tool: return 0xE01B
        case .plug: return 0xE01C
        case .memory: return 0xE01D
        case .taskList: return 0xE01E
        case .reminder: return 0xE01F
        case .sparkle: return 0xE020
        case .plan: return 0xE021
        case .workflow: return 0xE022
        case .automation: return 0xE023
        case .trigger: return 0xE024
        case .approval: return 0xE025
        case .permission: return 0xE026
        case .handoff: return 0xE027
        case .skill: return 0xE028
        case .knowledge: return 0xE029
        case .context: return 0xE02A
        case .source: return 0xE02B
        case .citation: return 0xE02C
        case .prompt: return 0xE02D
        case .model: return 0xE02E
        case .backgroundTask: return 0xE02F
        case .back: return 0xE030
        case .forward: return 0xE031
        case .up: return 0xE032
        case .down: return 0xE033
        case .chevronLeft: return 0xE034
        case .chevronRight: return 0xE035
        case .chevronUp: return 0xE036
        case .chevronDown: return 0xE037
        case .arrowUpRight: return 0xE038
        case .arrowDownLeft: return 0xE039
        case .arrowUpLeft: return 0xE03A
        case .arrowDownRight: return 0xE03B
        case .doubleChevronLeft: return 0xE03C
        case .doubleChevronRight: return 0xE03D
        case .expand: return 0xE03E
        case .collapse: return 0xE03F
        case .fullscreen: return 0xE040
        case .exitFullscreen: return 0xE041
        case .home: return 0xE042
        case .menu: return 0xE043
        case .moreHorizontal: return 0xE044
        case .moreVertical: return 0xE045
        case .close: return 0xE046
        case .sidebarLeft: return 0xE047
        case .sidebarRight: return 0xE048
        case .grid: return 0xE049
        case .list: return 0xE04A
        case .dashboard: return 0xE04B
        case .tabs: return 0xE04C
        case .window: return 0xE04D
        case .newWindow: return 0xE04E
        case .splitView: return 0xE04F
        case .check: return 0xE050
        case .checkCircle: return 0xE051
        case .info: return 0xE052
        case .warning: return 0xE053
        case .error: return 0xE054
        case .help: return 0xE055
        case .loading: return 0xE056
        case .progress: return 0xE057
        case .offline: return 0xE058
        case .online: return 0xE059
        case .sync: return 0xE05A
        case .verified: return 0xE05B
        case .new: return 0xE05C
        case .beta: return 0xE05D
        case .badge: return 0xE05E
        case .notificationDot: return 0xE05F
        case .pending: return 0xE060
        case .timeout: return 0xE061
        case .bell: return 0xE062
        case .file: return 0xE063
        case .newFile: return 0xE064
        case .folder: return 0xE065
        case .newFolder: return 0xE066
        case .document: return 0xE067
        case .spreadsheet: return 0xE068
        case .presentation: return 0xE069
        case .pdf: return 0xE06A
        case .imageFile: return 0xE06B
        case .audioFile: return 0xE06C
        case .videoFile: return 0xE06D
        case .codeFile: return 0xE06E
        case .archive: return 0xE06F
        case .link: return 0xE070
        case .unlink: return 0xE071
        case .share: return 0xE072
        case .export: return 0xE073
        case .`import`: return 0xE074
        case .download: return 0xE075
        case .upload: return 0xE076
        case .bookmark: return 0xE077
        case .tag: return 0xE078
        case .star: return 0xE079
        case .note: return 0xE07A
        case .clipboard: return 0xE07B
        case .trash: return 0xE07C
        case .restore: return 0xE07D
        case .history: return 0xE07E
        case .version: return 0xE07F
        case .compare: return 0xE080
        case .template: return 0xE081
        case .print: return 0xE082
        case .save: return 0xE083
        case .duplicate: return 0xE084
        case .rename: return 0xE085
        case .label: return 0xE086
        case .search: return 0xE087
        case .zoomIn: return 0xE088
        case .zoomOut: return 0xE089
        case .filter: return 0xE08A
        case .sort: return 0xE08B
        case .sortAscending: return 0xE08C
        case .sortDescending: return 0xE08D
        case .findInPage: return 0xE08E
        case .recent: return 0xE08F
        case .savedSearch: return 0xE090
        case .advancedSearch: return 0xE091
        case .clear: return 0xE092
        case .settings: return 0xE093
        case .sliders: return 0xE094
        case .toggleOn: return 0xE095
        case .toggleOff: return 0xE096
        case .theme: return 0xE097
        case .darkMode: return 0xE098
        case .lightMode: return 0xE099
        case .autoMode: return 0xE09A
        case .fontSize: return 0xE09B
        case .language: return 0xE09C
        case .accessibility: return 0xE09D
        case .notificationSettings: return 0xE09E
        case .privacySettings: return 0xE09F
        case .dataControls: return 0xE0A0
        case .profile: return 0xE0A1
        case .account: return 0xE0A2
        case .lock: return 0xE0A3
        case .unlock: return 0xE0A4
        case .key: return 0xE0A5
        case .passkey: return 0xE0A6
        case .password: return 0xE0A7
        case .shieldCheck: return 0xE0A8
        case .shieldAlert: return 0xE0A9
        case .eye: return 0xE0AA
        case .eyeOff: return 0xE0AB
        case .incognito: return 0xE0AC
        case .encryption: return 0xE0AD
        case .consent: return 0xE0AE
        case .auditLog: return 0xE0AF
        case .block: return 0xE0B0
        case .reportFlag: return 0xE0B1
        case .twoFactor: return 0xE0B2
        case .cloud: return 0xE0B3
        case .cloudUpload: return 0xE0B4
        case .cloudDownload: return 0xE0B5
        case .cloudOff: return 0xE0B6
        case .backup: return 0xE0B7
        case .restoreBackup: return 0xE0B8
        case .syncNow: return 0xE0B9
        case .autoSync: return 0xE0BA
        case .syncPaused: return 0xE0BB
        case .syncError: return 0xE0BC
        case .signIn: return 0xE0BD
        case .signOut: return 0xE0BE
        case .switchAccount: return 0xE0BF
        case .addAccount: return 0xE0C0
        case .upgrade: return 0xE0C1
        case .helpCenter: return 0xE0C2
        case .feedback: return 0xE0C3
        case .support: return 0xE0C4
        case .reportAProblem: return 0xE0C5
        case .about: return 0xE0C6
        case .whatsNew: return 0xE0C7
        case .tutorial: return 0xE0C8
        case .tips: return 0xE0C9
        case .shareApp: return 0xE0CA
        case .rateApp: return 0xE0CB
        case .legal: return 0xE0CC
        case .code: return 0xE0CD
        case .terminal: return 0xE0CE
        case .codeBlock: return 0xE0CF
        case .runCode: return 0xE0D0
        case .branch: return 0xE0D1
        case .starFilled: return 0xE0D2
        case .bookmarkFilled: return 0xE0D3
        case .pinFilled: return 0xE0D4
        case .thumbsUpFilled: return 0xE0D5
        case .thumbsDownFilled: return 0xE0D6
        case .bellFilled: return 0xE0D7
        case .micFilled: return 0xE0D8
        case .stopFilled: return 0xE0D9
        case .computer: return 0xE0DA
        case .laptop: return 0xE0DB
        case .phone: return 0xE0DC
        case .tablet: return 0xE0DD
        case .watch: return 0xE0DE
        case .devices: return 0xE0DF
        case .browser: return 0xE0E0
        case .brain: return 0xE0E1
        case .webSearch: return 0xE0E2
        case .deepResearch: return 0xE0E3
        case .project: return 0xE0E4
        case .artifact: return 0xE0E5
        case .summarize: return 0xE0E6
        case .translate: return 0xE0E7
        case .computerUse: return 0xE0E8
        case .screenShare: return 0xE0E9
        case .`extension`: return 0xE0EA
        case .api: return 0xE0EB
        case .server: return 0xE0EC
        case .chat: return 0xE0ED
        case .newChat: return 0xE0EE
        case .conversations: return 0xE0EF
        case .editMessage: return 0xE0F0
        case .readReceipt: return 0xE0F1
        case .scheduleSend: return 0xE0F2
        case .hashtag: return 0xE0F3
        case .keyboard: return 0xE0F4
        case .command: return 0xE0F5
        case .usage: return 0xE0F6
        case .appearance: return 0xE0F7
        case .billing: return 0xE0F8
        case .receipt: return 0xE0F9
        case .wallet: return 0xE0FA
        case .subscription: return 0xE0FB
        case .faceId: return 0xE0FC
        case .fingerprint: return 0xE0FD
        case .qrCode: return 0xE0FE
        case .scan: return 0xE0FF
        case .calendar: return 0xE100
        case .scheduledTask: return 0xE101
        case .timer: return 0xE102
        case .location: return 0xE103
        case .map: return 0xE104
        case .play: return 0xE105
        case .pause: return 0xE106
        case .volume: return 0xE107
        case .mute: return 0xE108
        case .headphones: return 0xE109
        case .readAloud: return 0xE10A
        case .subtitles: return 0xE10B
        case .record: return 0xE10C
        case .barChart: return 0xE10D
        case .lineChart: return 0xE10E
        case .pieChart: return 0xE10F
        case .trendingUp: return 0xE110
        case .mail: return 0xE111
        case .inbox: return 0xE112
        case .phoneCall: return 0xE113
        case .contacts: return 0xE114
        case .dragHandle: return 0xE115
        case .heart: return 0xE116
        case .bug: return 0xE117
        case .heartFilled: return 0xE118
        case .playFilled: return 0xE119
        }
    }

    /// A short English name for VoiceOver. (Not called `label`, because one symbol is named label.)
    public var accessibilityLabel: String {
        switch self {
        case .send: return "Send"
        case .stop: return "Stop"
        case .mic: return "Microphone"
        case .micOff: return "Microphone off"
        case .attach: return "Attach"
        case .image: return "Image"
        case .camera: return "Camera"
        case .copy: return "Copy"
        case .paste: return "Paste"
        case .cut: return "Cut"
        case .retry: return "Retry"
        case .regenerate: return "Regenerate"
        case .edit: return "Edit"
        case .delete: return "Delete"
        case .reply: return "Reply"
        case .forwardMessage: return "Forward message"
        case .quote: return "Quote"
        case .pin: return "Pin"
        case .unpin: return "Unpin"
        case .mention: return "Mention"
        case .emoji: return "Emoji"
        case .thumbsUp: return "Thumbs up"
        case .thumbsDown: return "Thumbs down"
        case .voiceMessage: return "Voice message"
        case .agent: return "Agent"
        case .user: return "User"
        case .team: return "Team"
        case .tool: return "Tool"
        case .plug: return "Plug"
        case .memory: return "Memory"
        case .taskList: return "Task list"
        case .reminder: return "Reminder"
        case .sparkle: return "Sparkle"
        case .plan: return "Plan"
        case .workflow: return "Workflow"
        case .automation: return "Automation"
        case .trigger: return "Trigger"
        case .approval: return "Approval"
        case .permission: return "Permission"
        case .handoff: return "Handoff"
        case .skill: return "Skill"
        case .knowledge: return "Knowledge"
        case .context: return "Context"
        case .source: return "Source"
        case .citation: return "Citation"
        case .prompt: return "Prompt"
        case .model: return "Model"
        case .backgroundTask: return "Background task"
        case .back: return "Back"
        case .forward: return "Forward"
        case .up: return "Up arrow"
        case .down: return "Down arrow"
        case .chevronLeft: return "Chevron left"
        case .chevronRight: return "Chevron right"
        case .chevronUp: return "Chevron up"
        case .chevronDown: return "Chevron down"
        case .arrowUpRight: return "Arrow up right"
        case .arrowDownLeft: return "Arrow down left"
        case .arrowUpLeft: return "Arrow up left"
        case .arrowDownRight: return "Arrow down right"
        case .doubleChevronLeft: return "Double chevron left"
        case .doubleChevronRight: return "Double chevron right"
        case .expand: return "Expand"
        case .collapse: return "Collapse"
        case .fullscreen: return "Fullscreen"
        case .exitFullscreen: return "Exit fullscreen"
        case .home: return "Home"
        case .menu: return "Menu"
        case .moreHorizontal: return "More options"
        case .moreVertical: return "More options, vertical"
        case .close: return "Close"
        case .sidebarLeft: return "Sidebar left"
        case .sidebarRight: return "Sidebar right"
        case .grid: return "Grid"
        case .list: return "List"
        case .dashboard: return "Dashboard"
        case .tabs: return "Tabs"
        case .window: return "Window"
        case .newWindow: return "New window"
        case .splitView: return "Split view"
        case .check: return "Check"
        case .checkCircle: return "Check circle"
        case .info: return "Information"
        case .warning: return "Warning"
        case .error: return "Error"
        case .help: return "Help"
        case .loading: return "Loading"
        case .progress: return "Progress"
        case .offline: return "Offline"
        case .online: return "Online"
        case .sync: return "Sync"
        case .verified: return "Verified"
        case .new: return "New"
        case .beta: return "Beta"
        case .badge: return "Badge"
        case .notificationDot: return "Notification dot"
        case .pending: return "Pending"
        case .timeout: return "Timeout"
        case .bell: return "Bell"
        case .file: return "File"
        case .newFile: return "New file"
        case .folder: return "Folder"
        case .newFolder: return "New folder"
        case .document: return "Document"
        case .spreadsheet: return "Spreadsheet"
        case .presentation: return "Presentation"
        case .pdf: return "PDF"
        case .imageFile: return "Image file"
        case .audioFile: return "Audio file"
        case .videoFile: return "Video file"
        case .codeFile: return "Code file"
        case .archive: return "Archive"
        case .link: return "Link"
        case .unlink: return "Unlink"
        case .share: return "Share"
        case .export: return "Export"
        case .`import`: return "Import"
        case .download: return "Download"
        case .upload: return "Upload"
        case .bookmark: return "Bookmark"
        case .tag: return "Tag"
        case .star: return "Star"
        case .note: return "Note"
        case .clipboard: return "Clipboard"
        case .trash: return "Trash"
        case .restore: return "Restore"
        case .history: return "History"
        case .version: return "Version"
        case .compare: return "Compare"
        case .template: return "Template"
        case .print: return "Print"
        case .save: return "Save"
        case .duplicate: return "Duplicate"
        case .rename: return "Rename"
        case .label: return "Label"
        case .search: return "Search"
        case .zoomIn: return "Zoom in"
        case .zoomOut: return "Zoom out"
        case .filter: return "Filter"
        case .sort: return "Sort"
        case .sortAscending: return "Sort ascending"
        case .sortDescending: return "Sort descending"
        case .findInPage: return "Find in page"
        case .recent: return "Recent"
        case .savedSearch: return "Saved search"
        case .advancedSearch: return "Advanced search"
        case .clear: return "Clear"
        case .settings: return "Settings"
        case .sliders: return "Sliders"
        case .toggleOn: return "Toggle on"
        case .toggleOff: return "Toggle off"
        case .theme: return "Theme"
        case .darkMode: return "Dark mode"
        case .lightMode: return "Light mode"
        case .autoMode: return "Auto mode"
        case .fontSize: return "Font size"
        case .language: return "Language"
        case .accessibility: return "Accessibility"
        case .notificationSettings: return "Notification settings"
        case .privacySettings: return "Privacy settings"
        case .dataControls: return "Data controls"
        case .profile: return "Profile"
        case .account: return "Account"
        case .lock: return "Lock"
        case .unlock: return "Unlock"
        case .key: return "Key"
        case .passkey: return "Passkey"
        case .password: return "Password"
        case .shieldCheck: return "Shield check"
        case .shieldAlert: return "Shield alert"
        case .eye: return "Eye"
        case .eyeOff: return "Eye off"
        case .incognito: return "Incognito"
        case .encryption: return "Encryption"
        case .consent: return "Consent"
        case .auditLog: return "Audit log"
        case .block: return "Block"
        case .reportFlag: return "Report flag"
        case .twoFactor: return "Two-factor authentication"
        case .cloud: return "Cloud"
        case .cloudUpload: return "Cloud upload"
        case .cloudDownload: return "Cloud download"
        case .cloudOff: return "Cloud off"
        case .backup: return "Backup"
        case .restoreBackup: return "Restore backup"
        case .syncNow: return "Sync now"
        case .autoSync: return "Auto sync"
        case .syncPaused: return "Sync paused"
        case .syncError: return "Sync error"
        case .signIn: return "Sign in"
        case .signOut: return "Sign out"
        case .switchAccount: return "Switch account"
        case .addAccount: return "Add account"
        case .upgrade: return "Upgrade"
        case .helpCenter: return "Help center"
        case .feedback: return "Feedback"
        case .support: return "Support"
        case .reportAProblem: return "Report a problem"
        case .about: return "About"
        case .whatsNew: return "What's new"
        case .tutorial: return "Tutorial"
        case .tips: return "Tips"
        case .shareApp: return "Share app"
        case .rateApp: return "Rate app"
        case .legal: return "Legal"
        case .code: return "Code"
        case .terminal: return "Terminal"
        case .codeBlock: return "Code block"
        case .runCode: return "Run code"
        case .branch: return "Branch"
        case .starFilled: return "Star, active"
        case .bookmarkFilled: return "Bookmark, active"
        case .pinFilled: return "Pin, active"
        case .thumbsUpFilled: return "Thumbs up, active"
        case .thumbsDownFilled: return "Thumbs down, active"
        case .bellFilled: return "Bell, active"
        case .micFilled: return "Microphone, active"
        case .stopFilled: return "Stop, active"
        case .computer: return "Computer"
        case .laptop: return "Laptop"
        case .phone: return "Phone"
        case .tablet: return "Tablet"
        case .watch: return "Watch"
        case .devices: return "Devices"
        case .browser: return "Browser"
        case .brain: return "Brain"
        case .webSearch: return "Web search"
        case .deepResearch: return "Deep research"
        case .project: return "Project"
        case .artifact: return "Artifact"
        case .summarize: return "Summarize"
        case .translate: return "Translate"
        case .computerUse: return "Computer use"
        case .screenShare: return "Screen share"
        case .`extension`: return "Extension"
        case .api: return "Api"
        case .server: return "Server"
        case .chat: return "Chat"
        case .newChat: return "New chat"
        case .conversations: return "Conversations"
        case .editMessage: return "Edit message"
        case .readReceipt: return "Read receipt"
        case .scheduleSend: return "Schedule send"
        case .hashtag: return "Hashtag"
        case .keyboard: return "Keyboard"
        case .command: return "Command"
        case .usage: return "Usage"
        case .appearance: return "Appearance"
        case .billing: return "Billing"
        case .receipt: return "Receipt"
        case .wallet: return "Wallet"
        case .subscription: return "Subscription"
        case .faceId: return "Face id"
        case .fingerprint: return "Fingerprint"
        case .qrCode: return "Qr code"
        case .scan: return "Scan"
        case .calendar: return "Calendar"
        case .scheduledTask: return "Scheduled task"
        case .timer: return "Timer"
        case .location: return "Location"
        case .map: return "Map"
        case .play: return "Play"
        case .pause: return "Pause"
        case .volume: return "Volume"
        case .mute: return "Mute"
        case .headphones: return "Headphones"
        case .readAloud: return "Read aloud"
        case .subtitles: return "Subtitles"
        case .record: return "Record"
        case .barChart: return "Bar chart"
        case .lineChart: return "Line chart"
        case .pieChart: return "Pie chart"
        case .trendingUp: return "Trending up"
        case .mail: return "Mail"
        case .inbox: return "Inbox"
        case .phoneCall: return "Phone call"
        case .contacts: return "Contacts"
        case .dragHandle: return "Drag handle"
        case .heart: return "Heart"
        case .bug: return "Bug"
        case .heartFilled: return "Heart, active"
        case .playFilled: return "Play, active"
        }
    }

    /// True for direction symbols (send, back, reply ...) that mirror in right-to-left languages.
    public var mirrorsInRightToLeft: Bool {
        switch self {
        case .send, .reply, .forwardMessage, .taskList, .handoff, .back, .forward, .chevronLeft, .chevronRight, .arrowUpRight, .arrowDownLeft, .arrowUpLeft, .arrowDownRight, .doubleChevronLeft, .doubleChevronRight, .sidebarLeft, .sidebarRight, .list, .newWindow, .share, .export, .`import`, .restore, .history, .sortAscending, .sortDescending, .auditLog, .restoreBackup, .signIn, .signOut, .shareApp, .scheduleSend, .play, .volume, .mute, .readAloud, .trendingUp, .playFilled: return true
        default: return false
        }
    }

    /// The symbol as a one-character string in the Admiralty Symbols font.
    public var character: String {
        String(Character(Unicode.Scalar(codepoint)!))
    }
}

// MARK: - Weights and families

/// The three weights of every Admiralty family. For symbols, match the text next to the icon:
/// regular for body text, medium for buttons and labels, bold for bold text.
public enum AdmiraltyWeight: Sendable {
    case regular, medium, bold

    fileprivate var styleName: String {
        switch self {
        case .regular: return "Regular"
        case .medium: return "Medium"
        case .bold: return "Bold"
        }
    }

    /// The PostScript name of the Admiralty Symbols font in this weight.
    public var symbolsPostScriptName: String { "AdmiraltySymbols-" + styleName }
}

/// The three text families. Sans: interface and the user's messages. Serif: the agent's
/// messages (same widths as Sans, so switching never changes line breaks). Mono: code and IDs.
public enum AdmiraltyFamily: Sendable {
    case sans, serif, mono

    fileprivate var postScriptFamily: String {
        switch self {
        case .sans: return "AdmiraltySans"
        case .serif: return "AdmiraltySerif"
        case .mono: return "AdmiraltyMono"
        }
    }

    /// The PostScript name of one style, e.g. "AdmiraltySerif-MediumItalic".
    public func postScriptName(weight: AdmiraltyWeight = .regular, italic: Bool = false) -> String {
        let style: String
        switch (weight, italic) {
        case (.regular, false): style = "Regular"
        case (.regular, true): style = "Italic"
        case (_, false): style = weight.styleName
        case (_, true): style = weight.styleName + "Italic"
        }
        return postScriptFamily + "-" + style
    }
}

// MARK: - Font registration

public enum Admiralty {
    /// Registers all Admiralty fonts that ship inside this package (Sans, Serif, Mono and Symbols,
    /// 21 styles). Every helper calls it; call it yourself before using a font by name in UIKit.
    public static func registerFonts() {
        _ = registered
    }

    private static let registered: Bool = {
        for url in Bundle.module.urls(forResourcesWithExtension: "ttf", subdirectory: "Fonts") ?? [] {
            CTFontManagerRegisterFontsForURL(url as CFURL, .process, nil)
        }
        return true
    }()
}

// MARK: - Text fonts

public extension Font {
    /// An Admiralty text font that scales with Dynamic Type:
    /// `.font(.admiralty(.serif, size: 17))`, `.font(.admiralty(.mono, size: 14, relativeTo: .callout))`.
    static func admiralty(_ family: AdmiraltyFamily = .sans, size: CGFloat, relativeTo textStyle: Font.TextStyle = .body,
                          weight: AdmiraltyWeight = .regular, italic: Bool = false) -> Font {
        Admiralty.registerFonts()
        return .custom(family.postScriptName(weight: weight, italic: italic), size: size, relativeTo: textStyle)
    }
}

#if canImport(UIKit)
public extension UIFont {
    /// An Admiralty text font for UIKit, scaled for the user's text size setting.
    static func admiralty(_ family: AdmiraltyFamily = .sans, size: CGFloat, textStyle: UIFont.TextStyle = .body,
                          weight: AdmiraltyWeight = .regular, italic: Bool = false) -> UIFont {
        Admiralty.registerFonts()
        let base = UIFont(name: family.postScriptName(weight: weight, italic: italic), size: size)
            ?? UIFont.systemFont(ofSize: size)
        return UIFontMetrics(forTextStyle: textStyle).scaledFont(for: base)
    }
}
#endif

// MARK: - SwiftUI

public extension Text {
    /// An Admiralty symbol as text. It scales with Dynamic Type, sits on the text baseline and
    /// takes the foreground colour, so it can be joined with other text:
    /// `Text(admiralty: .heartFilled) + Text(" Liked")`.
    init(admiralty symbol: AdmiraltySymbol, size: CGFloat = 17, relativeTo textStyle: Font.TextStyle = .body,
         weight: AdmiraltyWeight = .regular) {
        Admiralty.registerFonts()
        self = Text(verbatim: symbol.character)
            .font(.custom(weight.symbolsPostScriptName, size: size, relativeTo: textStyle))
    }

    /// The same, by name, like `Image(systemName:)`. An unknown name gives empty text.
    init(admiralty name: String, size: CGFloat = 17, relativeTo textStyle: Font.TextStyle = .body,
         weight: AdmiraltyWeight = .regular) {
        Admiralty.registerFonts()
        self = Text(verbatim: AdmiraltySymbol(rawValue: name)?.character ?? "")
            .font(.custom(weight.symbolsPostScriptName, size: size, relativeTo: textStyle))
    }
}

/// A ready-made icon view: scales with Dynamic Type, mirrors in right-to-left layouts when the
/// symbol should, and reads its name to VoiceOver.
///
///     AdmiraltyIcon("heart-filled")
///     AdmiraltyIcon(.send, size: 20, weight: .medium).foregroundStyle(.blue)
public struct AdmiraltyIcon: View {
    private let symbol: AdmiraltySymbol?
    private let size: CGFloat
    private let textStyle: Font.TextStyle
    private let weight: AdmiraltyWeight

    public init(_ symbol: AdmiraltySymbol, size: CGFloat = 17, relativeTo textStyle: Font.TextStyle = .body,
                weight: AdmiraltyWeight = .regular) {
        self.symbol = symbol
        self.size = size
        self.textStyle = textStyle
        self.weight = weight
    }

    public init(_ name: String, size: CGFloat = 17, relativeTo textStyle: Font.TextStyle = .body,
                weight: AdmiraltyWeight = .regular) {
        self.symbol = AdmiraltySymbol(rawValue: name)
        self.size = size
        self.textStyle = textStyle
        self.weight = weight
    }

    public var body: some View {
        if let symbol = symbol {
            Text(admiralty: symbol, size: size, relativeTo: textStyle, weight: weight)
                .flipsForRightToLeftLayoutDirection(symbol.mirrorsInRightToLeft)
                .accessibilityLabel(Text(symbol.accessibilityLabel))
        }
    }
}

#if canImport(UIKit)
public extension Image {
    /// An Admiralty symbol as a template image (it takes the tint or foreground colour).
    /// Its size is fixed by `pointSize`; use `Text(admiralty:)` or `AdmiraltyIcon` for an icon
    /// that grows with Dynamic Type.
    init(admiralty symbol: AdmiraltySymbol, pointSize: CGFloat = 17, weight: AdmiraltyWeight = .regular) {
        self = Image(uiImage: UIImage.admiralty(symbol, pointSize: pointSize, weight: weight))
            .renderingMode(.template)
    }

    /// The same, by name. An unknown name gives an empty image.
    init(admiralty name: String, pointSize: CGFloat = 17, weight: AdmiraltyWeight = .regular) {
        if let symbol = AdmiraltySymbol(rawValue: name) {
            self.init(admiralty: symbol, pointSize: pointSize, weight: weight)
        } else {
            self = Image(uiImage: UIImage())
        }
    }
}

// MARK: - UIKit

public extension UIImage {
    /// An Admiralty symbol as a template UIImage, for UIImageView, UIButton, tab bars and so on.
    /// The image is the symbol's full 24 x 24 grid box, so all symbols line up.
    static func admiralty(_ symbol: AdmiraltySymbol, pointSize: CGFloat = 17,
                          weight: AdmiraltyWeight = .regular) -> UIImage {
        Admiralty.registerFonts()
        let font = UIFont(name: weight.symbolsPostScriptName, size: pointSize) ?? UIFont.systemFont(ofSize: pointSize)
        // The symbol grid is 864 units square (24 x 36), from x = -12 and from 782 above the baseline.
        let side = (pointSize * 0.864).rounded(.up)
        let renderer = UIGraphicsImageRenderer(size: CGSize(width: side, height: side))
        let image = renderer.image { _ in
            let attributes: [NSAttributedString.Key: Any] = [.font: font, .foregroundColor: UIColor.black]
            let origin = CGPoint(x: pointSize * 0.012, y: pointSize * 0.782 - font.ascender)
            (symbol.character as NSString).draw(at: origin, withAttributes: attributes)
        }
        let template = image.withRenderingMode(.alwaysTemplate)
        return symbol.mirrorsInRightToLeft ? template.imageFlippedForRightToLeftLayoutDirection() : template
    }

    /// The same, by name, like `UIImage(systemName:)`. Returns nil for an unknown name.
    static func admiralty(named name: String, pointSize: CGFloat = 17,
                          weight: AdmiraltyWeight = .regular) -> UIImage? {
        guard let symbol = AdmiraltySymbol(rawValue: name) else { return nil }
        return admiralty(symbol, pointSize: pointSize, weight: weight)
    }
}
#endif
