// swift-tools-version:5.7
// Admiralty Symbols for iOS. Add this repository in Xcode (File > Add Package Dependencies).
import PackageDescription

let package = Package(
    name: "AdmiraltySymbols",
    platforms: [.iOS(.v15)],
    products: [.library(name: "AdmiraltySymbols", targets: ["AdmiraltySymbols"])],
    targets: [
        .target(name: "AdmiraltySymbols", path: "packages/ios/AdmiraltySymbols/Sources/AdmiraltySymbols",
                resources: [.copy("Fonts")])
    ]
)
